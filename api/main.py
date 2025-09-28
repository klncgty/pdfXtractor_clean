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


@app.post("/upload")
async def upload_pdf(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"filename": file.filename, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.get("/process/{filename}")
async def process_pdf(
    filename: str,
    output_format: str = "json",
    pages_limit: int = 30,  # Default 30
    request: Request = None,  # Session için
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Processing request for file: {filename}")
    logger.debug(f"Output format: {output_format}, Pages limit: {pages_limit}")
    
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
        
    # Pages limit validation
    try:
        pages_limit = int(pages_limit)
        if pages_limit < 1:
            raise ValueError("Pages limit must be positive")
    except ValueError as e:
        logger.error(f"Invalid pages limit: {pages_limit}")
        raise HTTPException(status_code=400, detail=str(e))
    
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
                logger.info(f"Setting default monthly page limit to 30 for user {user.id}")
            
            # Kota kontrolü
            pages_left = user.monthly_page_limit - user.pages_processed_this_month
            if pages_left <= 0:
                raise HTTPException(
                    status_code=403, 
                    detail=f'Monthly quota exceeded. Monthly limit is 30 pages, you have processed {user.pages_processed_this_month} pages this month.'
                )
            
            # İstenen sayfa sayısını kota limitine göre ayarla
            pages_limit = min(pages_limit, pages_left)
            logger.info(f"User has {pages_left} pages left in quota, will process {pages_limit} pages")
            
            # PDF'i yükle ve işle
            logger.debug("Initializing PDFTableProcessor...")
            processor = PDFTableProcessor(file_path)
            logger.info(f"PDF loaded successfully")
                
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
        if total_pages > pages_limit:
            warning_message = f"PDF contains {total_pages} pages, but only the first {pages_limit} pages will be processed due to monthly quota limit."
            
        # Pass pages_limit through to processor
        try:
            logger.debug(f"Starting to process tables with format: {output_format}, pages_limit: {pages_limit}")
            processed_tables = 0
            
            for result in processor.process_tables(output_format, pages_limit=pages_limit):
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
                    logger.debug(f"Successfully processed table {processed_tables}")
                    
                except Exception as table_error:
                    logger.error(f"Error processing table {processed_tables + 1}: {str(table_error)}", exc_info=True)
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error processing table {processed_tables + 1}: {str(table_error)}"
                    )

            if not results:
                raise HTTPException(
                    status_code=400, 
                    detail="No tables were successfully processed in the PDF"
                )
                
            logger.info(f"Successfully processed {processed_tables} tables")
            
        except Exception as process_error:
            logger.error(f"Error during table processing: {str(process_error)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error processing tables: {str(process_error)}"
            )

        # Kota harca
        user.pages_processed_this_month += pages_limit
        await db.commit()

        response_data = {
            "tables": results,
            "total_tables": processor.total_tables,
            "total_pages": total_pages,
            "processed_pages": min(total_pages, pages_limit)
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