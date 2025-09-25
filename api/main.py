from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List,Union, Dict, Any
import os
import shutil
from table_format import PDFTableProcessor
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
        
app = FastAPI(title="PDF Table Processor API")

# Early session middleware (restored per request)
app.add_middleware(SessionMiddleware, secret_key="cagatay-uygulama-secret-anahtari-2024")

# CORS middleware configuration
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Cookie", "Set-Cookie"],
    expose_headers=["Set-Cookie"],
    max_age=3600
)

# Session middleware - CORS'dan sonra eklenmeli
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "your-super-secret-key-change-in-production-123456789"),
    session_cookie="session_id",
    max_age=3600 * 24 * 7,  # 1 hafta
    same_site="lax",  # lax daha uyumlu
    https_only=False  # Development için False
)

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Database initialization - startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        print("🚀 Starting application...")
        print("📊 Initializing database...")
        await create_all_tables()
        print("✅ Database initialized successfully!")
        
        # Background tasks can be added here if needed
        print("✅ Application startup completed!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down application...")

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
async def process_pdf(filename: str, output_format: str = "json"):
    if output_format not in ["json", "csv", "both"]:
        raise HTTPException(status_code=400, detail="Invalid output format")
    
    file_path = f"uploads/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        processor = PDFTableProcessor(file_path)
        results = []
        
        for result in processor.process_tables(output_format):
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
        
        return {"tables": results, "total_tables": processor.total_tables}
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

#app.add_middleware(SessionMiddleware, secret_key="supersecretkey")
app.include_router(auth_router, prefix="/auth")
app.include_router(endpoints_router)

@app.on_event("startup")
async def start_tasks():
    # Ensure DB tables exist before starting background tasks
    await create_all_tables()
    asyncio.create_task(weekly_reset())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)