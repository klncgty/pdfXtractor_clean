from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User, PDF
from database import get_db
from pdf_utils import get_pdf_page_count
import os
import shutil
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads'))
print(f"Upload directory is: {UPLOAD_DIR}")
os.makedirs(UPLOAD_DIR, exist_ok=True)
print(f"Upload directory exists: {os.path.exists(UPLOAD_DIR)}")
print(f"Upload directory is writable: {os.access(UPLOAD_DIR, os.W_OK)}")

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail='Not authenticated')
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user

@router.post('/upload_pdf')
async def upload_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Dosyayı kaydet
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"File saved successfully at: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        print(f"File size: {os.path.getsize(file_path)} bytes")
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    # PDF sayfa sayısını bul
    pages_total = await get_pdf_page_count(file_path)

    # PDF kaydı oluştur (kota henüz harcanmıyor)
    pdf = PDF(
        user_id=user.id,
        pdf_filename=file.filename,
        pages_total=pages_total,
        pages_processed=0,  # Henüz işlenmedi
        uploaded_at=datetime.utcnow()
    )
    db.add(pdf)
    await db.commit()
    await db.refresh(pdf)

    return {
        'pdf_id': pdf.id,
        'pages_total': pages_total,
        'pages_processed': 0,  # Henüz kota harcanmadı
        'limit_left': user.monthly_page_limit - user.pages_processed_this_month
    }
