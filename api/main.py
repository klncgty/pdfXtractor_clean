from fastapi import FastAPI, UploadFile, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Union, Dict, Any
import os
import shutil
from contextlib import asynccontextmanager
from pydantic import BaseModel
from auth import router as auth_router
from endpoints import router as endpoints_router, get_current_user
import asyncio
from tasks import weekly_reset
from starlette.middleware.sessions import SessionMiddleware
from database import create_all_tables, get_db
from models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')

# In-memory cancellation flags for running processing jobs
CANCEL_FLAGS = {}
# In-memory progress tracking
PROCESS_PROGRESS = {}
PROCESS_TOTALS = {}
PROCESS_STATUS = {}


class QuestionRequest(BaseModel):
    question: Union[str, int, float]
    table: Union[str, Dict[str, Any], List[Dict[str, Any]]]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    try:
        print("Starting application...")
        print("Initializing database...")

        # Create necessary directories
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Optionally skip DB init and background tasks for quick dev/testing
        skip_db_init = os.getenv('SKIP_DB_INIT', '0') == '1'
        if skip_db_init:
            print("SKIP_DB_INIT=1 detected; skipping database initialization and background tasks (dev mode)")
        else:
            # Initialize database
            await create_all_tables()
            print("Database initialized successfully!")

            # Start background tasks
            print("Starting background tasks...")
            weekly_reset_task = asyncio.create_task(weekly_reset())

            print("Application startup completed!")

        yield  # Application is running

    except Exception as e:
        print(f"Startup failed: {e}")
        raise

    # Shutdown
    print("Shutting down application...")

    # Cancel background tasks if they exist
    try:
        if 'weekly_reset_task' in locals():
            weekly_reset_task.cancel()
            try:
                await weekly_reset_task
            except asyncio.CancelledError:
                print("Background task cancelled successfully")
    except Exception as e:
        print(f"Error during shutdown: {e}")

    print("Application shutdown completed!")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="PDF Table Processor API",
    lifespan=lifespan
)

# Exception handler to log all unhandled errors
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    import traceback
    error_msg = f"Unhandled error: {str(exc)}\n"
    error_msg += "".join(traceback.format_tb(exc.__traceback__))
    logger.error(error_msg)
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "traceback": traceback.format_exc()
        }
    )


# CORS middleware configuration
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174", 
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]

# Register CORSMiddleware before SessionMiddleware so preflight OPTIONS requests are handled
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Session middleware - add after CORS
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET") or ValueError("SESSION_SECRET environment variable eksik"),
    session_cookie="session_id",
    max_age=3600 * 24 * 7,
    same_site="lax",
    https_only=False
)
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running!"}


@app.get("/test-session")
async def test_session_endpoint(request: Request):
    """Test session functionality"""
    # Test session write
    request.session['test_key'] = 'test_value'
    request.session['timestamp'] = str(asyncio.get_event_loop().time())

    return {
        "message": "Session test successful",
        "session_data": dict(request.session),
        "cookies": dict(request.cookies)
    }





import logging
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.get("/process/{filename}")
async def process_pdf(
    filename: str,
    output_format: str = "json",
    start_page: int | None = None,
    end_page: int | None = None,
    request: Request = None,  # Session için
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Processing request for file: {filename}")
    logger.debug(f"Output format: {output_format}, Start Page: {start_page}, End Page: {end_page}")
    
    # Validate filename
    if not filename:
        logger.error("Filename is empty")
        raise HTTPException(status_code=400, detail='Filename is required')
        
    # Additional filename security checks
    if not filename.endswith('.pdf'):
        logger.error(f"Invalid file extension: {filename}")
        raise HTTPException(status_code=400, detail='Only PDF files are allowed')
        
    if '..' in filename or '/' in filename or '\\' in filename:
        logger.error(f"Invalid characters in filename: {filename}")
        raise HTTPException(status_code=400, detail='Invalid filename')
        
    # Output format validation
    if output_format not in ["json", "csv", "both"]:
        logger.error(f"Invalid output format: {output_format}")
        raise HTTPException(status_code=400, detail='Invalid output format')
        
    # Get current user from session
    user_id = request.session.get('user_id')
    if not user_id:
        logger.warning("No user_id found in session")
        raise HTTPException(status_code=401, detail='Not authenticated')
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        logger.warning(f"No user found for user_id: {user_id}")
        raise HTTPException(status_code=401, detail='User not found')

    if output_format not in ["json", "csv", "both"]:
        raise HTTPException(status_code=400, detail="Invalid output format")

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Validate file exists
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Initialize cancellation flag for this user's processing job
        processing_key = f"{user.id}:{filename}"
        CANCEL_FLAGS[processing_key] = False

        # 1. File checks
        logger.info(f"Starting to process PDF: {file_path}")
        try:
            if not os.path.exists(file_path):
                raise ValueError(f"File does not exist: {file_path}")
                
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                raise ValueError("File is empty")
            logger.debug(f"File size: {file_size} bytes")
            
            file_abs_path = os.path.abspath(file_path)
            logger.debug(f"File absolute path: {file_abs_path}")
            
            if not os.access(file_path, os.R_OK):
                raise ValueError(f"No read permission for file")
            if not os.access(os.path.dirname(file_path), os.W_OK):
                raise ValueError(f"No write permission for output directory")
                
            # Check if it's actually a PDF
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    raise ValueError("File is not a valid PDF")
                    
        except Exception as file_error:
            logger.error(f"File validation error: {str(file_error)}", exc_info=True)
            raise HTTPException(status_code=400, detail=str(file_error))
            
        # 2. Import and initialize PDFTableProcessor
        try:
            from table_format import PDFTableProcessor
            logger.info("PDFTableProcessor imported successfully")
        except ImportError as import_error:
            logger.error(f"Failed to import PDFTableProcessor: {str(import_error)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Internal server error: PDF processing module not available"
            )
        
    # 3. Process PDF
        try:
            # Aylık kota kontrolü - varsayılan 30 sayfa
            if user.monthly_page_limit != 30:
                user.monthly_page_limit = 30
                await db.commit()
                logger.info(f"Setting default monthly page limit to 30 for user {user.id}")
            
            # Check for active promotion
            from models import UserPromotion
            from datetime import datetime
            from sqlalchemy.orm import selectinload
            
            # Get user with promotion data
            result = await db.execute(
                select(User).options(selectinload(User.user_promotions)).where(User.id == user.id)
            )
            user_with_promos = result.scalars().first()
            
            # Check for active promotion
            has_active_promo = False
            for promo in user_with_promos.user_promotions:
                if promo.is_active and promo.expires_at > datetime.utcnow():
                    has_active_promo = True
                    break
            
            processor = PDFTableProcessor(file_path)
            total_pages_in_pdf = processor.total_pages

            # Determine pages to process
            pages_to_process = 0
            if start_page is not None and end_page is not None:
                if start_page > end_page:
                    raise HTTPException(status_code=400, detail="Start page cannot be greater than end page.")
                if start_page > total_pages_in_pdf:
                    raise HTTPException(status_code=400, detail=f"Start page {start_page} is out of bounds for a PDF with {total_pages_in_pdf} pages.")
                pages_to_process = (end_page - start_page) + 1
            elif start_page is not None:
                pages_to_process = 1
            else: # All pages
                pages_to_process = total_pages_in_pdf

            # Promo aktifse sınırsız, değilse normal kota kontrolü
            if has_active_promo:
                logger.info(f"User {user.id} has active promotion - unlimited processing")
            else:
                # Normal kota kontrolü
                pages_left = user.monthly_page_limit - user.pages_processed_this_month
                if pages_left <= 0:
                    raise HTTPException(
                        status_code=403, 
                        detail=f'Monthly quota exceeded. Monthly limit is {user.monthly_page_limit} pages, you have processed {user.pages_processed_this_month} pages this month.'
                    )
                
                if pages_to_process > pages_left:
                    logger.warning(f"User requested {pages_to_process} pages, but only has {pages_left} left in quota. Processing will be limited.")
                    # Adjust end_page based on quota
                    if start_page is not None:
                        end_page = min(end_page or total_pages_in_pdf, start_page + pages_left - 1)
                    else: # all pages mode
                        start_page = 1
                        end_page = pages_left
                    pages_to_process = pages_left

            logger.info(f"PDF loaded successfully")
            # Initialize progress tracking
            PROCESS_TOTALS[processing_key] = processor.total_tables
            PROCESS_PROGRESS[processing_key] = 0
            PROCESS_STATUS[processing_key] = 'running'
                
        except HTTPException:
            raise
        except Exception as processor_error:
            logger.error(f"PDF processing error: {str(processor_error)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error processing PDF: {str(processor_error)}"
            )
        
        results = []
        
        # Check total pages and set warning if needed
        total_pages = processor.total_pages
        warning_message = None
        if not has_active_promo and pages_to_process < total_pages:
             warning_message = f"PDF contains {total_pages} pages, but only {pages_to_process} pages will be processed due to monthly quota limit."

        # Pass page range to processor
        try:
            logger.debug(f"Starting to process tables with format: {output_format}, start_page: {start_page}, end_page: {end_page}")
            processed_tables = 0
            processed_pages_set = set()
            
            canceled = False
            for result in processor.process_tables(output_format, start_page=start_page, end_page=end_page):
                # Check if user requested cancellation
                if CANCEL_FLAGS.get(processing_key):
                    logger.info(f"Processing cancelled by user {user.id} for file {filename}")
                    canceled = True
                    break
                try:
                    if output_format == "both":
                        if len(result) != 3:
                            raise ValueError(f"Expected 3 files for 'both' format, got {len(result)}")
                        json_file, csv_file, image_file = result
                        
                        # Validate all files exist
                        for file_path in [json_file, csv_file, image_file]:
                            if not os.path.exists(file_path):
                                raise ValueError(f"Generated file does not exist: {file_path}")
                                
                        results.append({
                            "json_file": os.path.basename(json_file),
                            "csv_file": os.path.basename(csv_file),
                            "image_file": os.path.basename(image_file)
                        })
                    else:
                        if len(result) != 2:
                            raise ValueError(f"Expected 2 files for '{output_format}' format, got {len(result)}")
                        data_file, image_file = result
                        
                        # Validate files exist
                        for file_path in [data_file, image_file]:
                            if not os.path.exists(file_path):
                                raise ValueError(f"Generated file does not exist: {file_path}")
                                
                        results.append({
                            "data_file": os.path.basename(data_file),
                            "image_file": os.path.basename(image_file)
                        })
                    
                    processed_tables += 1
                    # Determine page index from generated filename and track unique pages
                    try:
                        # result contains file paths; first element is the data file (json or csv)
                        data_file_path = None
                        if output_format == "both":
                            data_file_path = json_file
                        else:
                            data_file_path = data_file
                        base = os.path.basename(data_file_path)
                        m = re.search(r'page_(\d+)_', base)
                        if m:
                            page_idx = int(m.group(1))
                            processed_pages_set.add(page_idx)
                    except Exception:
                        logger.debug("Could not parse page index from filename for quota accounting", exc_info=True)

                    # Update progress tracking (still count tables for progress)
                    PROCESS_PROGRESS[processing_key] = processed_tables
                    logger.debug(f"Successfully processed table {processed_tables}")
                    
                except Exception as table_error:
                    logger.error(f"Error processing table {processed_tables + 1}: {str(table_error)}", exc_info=True)
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error processing table {processed_tables + 1}: {str(table_error)}"
                    )

            if canceled:
                # Do not consume quota when cancelled
                logger.info(f"Processing cancelled before completion for {processing_key}; not consuming quota")
                # Clean up flag and set status
                CANCEL_FLAGS.pop(processing_key, None)
                PROCESS_STATUS[processing_key] = 'cancelled'
                # Return partial results to the client so frontend can show downloads for processed tables
                response_data = {
                    "tables": results,
                    "total_tables": processor.total_tables,
                    "total_pages": total_pages,
                    "processed_pages": len(processed_pages_set),
                    "processed_tables": processed_tables,
                    "cancelled": True
                }
                if warning_message:
                    response_data["warning"] = warning_message
                return response_data

            if not results:
                raise HTTPException(
                    status_code=400, 
                    detail="No tables were successfully processed in the PDF"
                )
                
            logger.info(f"Successfully processed {processed_tables} tables on {len(processed_pages_set)} pages")
            PROCESS_STATUS[processing_key] = 'finished'
            
        except Exception as process_error:
            logger.error(f"Error during table processing: {str(process_error)}", exc_info=True)
            PROCESS_STATUS[processing_key] = 'failed'
            raise HTTPException(
                status_code=500,
                detail=f"Error processing tables: {str(process_error)}"
            )

        # Kota harca - sadece promo yoksa (commit only after successful processing)
        if not has_active_promo:
            try:
                processed_pages_count = len(processed_pages_set)
                if processed_pages_count > 0:
                    user.pages_processed_this_month += processed_pages_count
                    await db.commit()
                    logger.info(f"Used {processed_pages_count} pages from quota for user {user.id}. New total: {user.pages_processed_this_month}")
                else:
                    logger.info("No pages with tables were processed, no quota consumed.")
            except Exception as e:
                logger.error(f"Failed to commit quota usage for user {user.id}: {e}", exc_info=True)
                await db.rollback() # Rollback on error
        else:
            logger.info(f"Unlimited promo active - no quota consumed")

        # Clean up cancellation flag on normal completion
        CANCEL_FLAGS.pop(processing_key, None)

        response_data = {
            "tables": results,
            "total_tables": processor.total_tables,
            "total_pages": total_pages,
            "processed_pages": len(processed_pages_set),
            "processed_tables": processed_tables
        }
        if warning_message:
            response_data["warning"] = warning_message
            
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.post("/cancel_processing")
async def cancel_processing(request: Request):
    """Endpoint for user to cancel an in-progress processing job.
    Expects JSON body: { "filename": "name.pdf" }
    """
    try:
        body = await request.json()
        filename = body.get('filename')
        user_id = request.session.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail='Not authenticated')
        if not filename:
            raise HTTPException(status_code=400, detail='filename is required')

        processing_key = f"{user_id}:{filename}"
        if processing_key in CANCEL_FLAGS:
            CANCEL_FLAGS[processing_key] = True
            return {"status": "cancel_requested"}
        else:
            return {"status": "no_active_job"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/process_status")
async def process_status(filename: str, request: Request):
    """Return current processing progress for the given filename for the session user."""
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail='Not authenticated')

        processing_key = f"{user_id}:{filename}"
        progress = PROCESS_PROGRESS.get(processing_key, 0)
        total = PROCESS_TOTALS.get(processing_key, 0)
        status = PROCESS_STATUS.get(processing_key, 'idle')

        return {
            'filename': filename,
            'progress': int(progress),
            'total': int(total),
            'status': status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        print("Received request:", request.model_dump_json())

        from q_a import ask_question
        print("-----------------")
        print("-----------------")
        print("-----------------")
        print("-----------------")
        print(request.table)
        answer = ask_question(request.question, request.table)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Include routers
app.include_router(auth_router, prefix="/auth")
app.include_router(endpoints_router)

# Include API router
from api_endpoints import router as api_router
app.include_router(api_router, prefix="/api")

# Include Stripe router
from stripe_endpoints import router as stripe_router
app.include_router(stripe_router, prefix="/stripe")

# Include Promotion router
from promo_endpoints import router as promo_router
app.include_router(promo_router)

# Static routes temporarily disabled
# Will be implemented later


if __name__ == "__main__":
    import uvicorn
    
    # Configure uvicorn logging
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "": {"handlers": ["default"], "level": "DEBUG"},
        },
    }
    
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_config=log_config)