from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Union, Dict, Any
import os
import shutil
from contextlib import asynccontextmanager
from pydantic import BaseModel
from auth import router as auth_router
from endpoints import router as endpoints_router
import asyncio
from tasks import weekly_reset
from starlette.middleware.sessions import SessionMiddleware
from database import create_all_tables


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
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("outputs", exist_ok=True)

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


# CORS middleware configuration
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
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

    file_path = f"uploads/{file.filename}"
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"filename": file.filename, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/process/{filename}")
async def process_pdf(filename: str, output_format: str = "json", pages_limit: int | None = None):
    """Process tables in the uploaded PDF. Optionally limit processing to `pages_limit` pages."""
    if output_format not in ["json", "csv", "both"]:
        raise HTTPException(status_code=400, detail="Invalid output format")

    file_path = f"uploads/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Lazy import because gmft is optional/heavy
        from table_format import PDFTableProcessor
        processor = PDFTableProcessor(file_path)
        results = []

        # Pass pages_limit through to processor
        for result in processor.process_tables(output_format, pages_limit=pages_limit):
            if output_format == "both":
                json_file, csv_file, image_file = result
                results.append({
                    "json_file": os.path.basename(json_file),
                    "csv_file": os.path.basename(csv_file),
                    "image_file": os.path.basename(image_file)
                })
            else:
                data_file, image_file = result
                results.append({
                    "data_file": os.path.basename(data_file),
                    "image_file": os.path.basename(image_file)
                })

        return {"tables": results, "total_tables": processor.total_tables, "total_pages": getattr(processor, 'total_pages', None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"outputs/{filename}"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)