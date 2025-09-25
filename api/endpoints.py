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

UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    # PDF sayfa sayısını bul
    pages_total = await get_pdf_page_count(file_path)
    pages_left = user.monthly_page_limit - user.pages_processed_this_month
    if pages_left <= 0:
        raise HTTPException(status_code=403, detail='Limit reached')
    pages_to_process = min(pages_total, pages_left)

    # PDF kaydı oluştur
    pdf = PDF(
        user_id=user.id,
        pdf_filename=file.filename,
        pages_total=pages_total,
        pages_processed=pages_to_process,
        uploaded_at=datetime.utcnow()
    )
    db.add(pdf)
    user.pages_processed_this_month += pages_to_process
    await db.commit()
    await db.refresh(pdf)
    await db.refresh(user)

    return {
        'pdf_id': pdf.id,
        'pages_total': pages_total,
        'pages_processed': pages_to_process,
        'limit_left': user.monthly_page_limit - user.pages_processed_this_month
    }
