from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from auth import verify_api_key
from models import User, APIKey
from table_format import PDFTableProcessor
import os
import tempfile
from typing import List, Optional
import asyncio

router = APIRouter()

@router.post("/v1/extract")
async def api_extract_tables(
    file: UploadFile = File(...),
    output_format: str = "both",  # json, csv, both
    pages_limit: Optional[int] = None,
    auth_data: dict = Depends(verify_api_key)
):
    """
    Public API endpoint for PDF table extraction
    
    Parameters:
    - file: PDF file to process
    - output_format: "json", "csv", or "both"
    - pages_limit: Maximum pages to process (optional)
    
    Returns:
    - JSON response with extraction results
    """
    
    api_key = auth_data["api_key"]
    user = auth_data["user"]
    
    # File validation
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Sadece PDF dosyaları desteklenir")
    
    if file.size > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="Dosya boyutu 50MB'dan küçük olmalı")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Initialize PDF processor
            processor = PDFTableProcessor(temp_file_path)
            
            # Process with page limit
            pages_to_process = min(pages_limit or 999, user.monthly_page_limit)
            tables_data = []
            pages_processed = 0
            
            # Get PDF info
            total_pages = processor.page_count
            
            for page_num in range(min(pages_to_process, total_pages)):
                page_tables = processor.per_page_tables.get(page_num, [])
                pages_processed = page_num + 1
                
                for table_idx, table in enumerate(page_tables):
                    try:
                        # Extract table data
                        extracted_data = processor.format_single_table(table)
                        
                        table_data = {
                            "page": page_num + 1,
                            "table_index": table_idx,
                            "data": extracted_data
                        }
                        
                        # Add format-specific data
                        if output_format in ['json', 'both']:
                            table_data["json_data"] = extracted_data
                        
                        if output_format in ['csv', 'both']:
                            # Convert to CSV format
                            import csv
                            import io
                            output = io.StringIO()
                            if extracted_data:
                                writer = csv.writer(output)
                                writer.writerows(extracted_data)
                                table_data["csv_data"] = output.getvalue()
                        
                        tables_data.append(table_data)
                        
                    except Exception as e:
                        print(f"Error processing table {table_idx} on page {page_num + 1}: {e}")
                        continue
            
            # Return structured response
            return {
                "success": True,
                "filename": file.filename,
                "pages_total": total_pages,
                "pages_processed": pages_processed,
                "tables_found": len(tables_data),
                "tables": tables_data,
                "api_usage": {
                    "requests_made_this_month": api_key.requests_made_this_month,
                    "monthly_request_limit": api_key.monthly_request_limit,
                    "remaining_requests": api_key.monthly_request_limit - api_key.requests_made_this_month
                }
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        print(f"API extraction error: {e}")
        raise HTTPException(status_code=500, detail=f"İşlem hatası: {str(e)}")

@router.get("/v1/usage")
async def get_api_usage(auth_data: dict = Depends(verify_api_key)):
    """Get current API usage statistics"""
    
    api_key = auth_data["api_key"]
    user = auth_data["user"]
    
    return {
        "api_key_name": api_key.name,
        "requests_made_this_month": api_key.requests_made_this_month,
        "monthly_request_limit": api_key.monthly_request_limit,
        "remaining_requests": api_key.monthly_request_limit - api_key.requests_made_this_month,
        "last_used": api_key.last_used,
        "user_quota": {
            "pages_processed_this_month": user.pages_processed_this_month,
            "monthly_page_limit": user.monthly_page_limit
        }
    }

@router.get("/v1/health")
async def api_health():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "api_version": "v1.0.0",
        "service": "Octro API"
    }