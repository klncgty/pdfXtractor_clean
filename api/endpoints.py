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
@router.post('/upload')  # İki URL'ye aynı endpoint hizmet veriyor
async def upload_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Dosya boyutu kontrolü (MB cinsinden)
    file_content = await file.read()
    file_size_mb = len(file_content) / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f}MB")
    
    # Kullanıcının planını kontrol et
    from models import Subscription
    result = await db.execute(select(Subscription).where(Subscription.user_id == user.id))
    subscription = result.scalars().first()
    print(f"User subscription: {subscription.plan_type if subscription else 'None'}")
    
    # Plan tipine göre upload limitlerini belirle
    if subscription and subscription.plan_type == 'pro':
        max_upload_mb = 100
    elif subscription and subscription.plan_type == 'standard':
        max_upload_mb = 50
    else:
        max_upload_mb = 10
    
    print(f"Max upload MB for user: {max_upload_mb}MB")
    
    # Dosya boyutu kontrolü
    if file_size_mb > max_upload_mb:
        plan_name = subscription.plan_type.title() if subscription else "Free"
        error_msg = f"File size ({file_size_mb:.1f}MB) exceeds {plan_name} plan limit of {max_upload_mb}MB"
        print(f"Upload rejected: {error_msg}")
        raise HTTPException(status_code=413, detail=error_msg)
    
    # Dosyayı kaydet
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, 'wb') as buffer:
            buffer.write(file_content)
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
    
    # Aktif promosyonu kontrol et
    from models import UserPromotion
    from sqlalchemy import and_
    
    # Kullanıcının aktif promosyonu var mı?
    result = await db.execute(
        select(UserPromotion).filter(
            and_(
                UserPromotion.user_id == user.id,
                UserPromotion.is_active == True,
                UserPromotion.expires_at > datetime.utcnow()
            )
        )
    )
    active_promo = result.scalars().first()
    
    # Eğer aktif promosyon varsa, sınırsız limit göster (9999)
    if active_promo:
        response_data = {
            'pdf_id': pdf.id,
            'pages_total': pages_total,
            'pages_processed': 0,
            'limit_left': 9999,  # Sınırsız limit göster
            'has_active_promo': True
        }
        print(f"Response with promo: {response_data}")
        return response_data
    else:
        # Normal kota
        limit_left = user.monthly_page_limit - user.pages_processed_this_month
        response_data = {
            'pdf_id': pdf.id,
            'pages_total': pages_total,
            'pages_processed': 0,
            'limit_left': limit_left,
            'has_active_promo': False
        }
        print(f"Response normal: {response_data}")
        return response_data
