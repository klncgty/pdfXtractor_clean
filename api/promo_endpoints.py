from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from datetime import datetime, timedelta
from typing import List, Optional
import os
import logging

from database import get_db
from models import User, PromotionCode, UserPromotion
from pydantic import BaseModel

# Logging'i yapılandır
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/promo", tags=["promotion"])

# Admin email - sadece bu email promosyon kodu üretebilir
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "cgtyklnc@gmail.com")


# Helper function to get current user
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    """Get current user from session"""
    user_id = request.session.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail='Not authenticated')
    
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user

class CreatePromoCodeRequest(BaseModel):
    description: Optional[str] = None
    max_uses: int = 1
    expires_in_days: Optional[int] = None  # Kodun geçerlilik süresi


class PromoCodeResponse(BaseModel):
    id: int
    code: str
    is_active: bool
    max_uses: int
    current_uses: int
    created_at: datetime
    expires_at: Optional[datetime]
    description: Optional[str]

    class Config:
        from_attributes = True


class ValidatePromoRequest(BaseModel):
    code: str


class ValidatePromoResponse(BaseModel):
    success: bool
    message: str


async def is_admin(current_user: User = Depends(get_current_user)):
    """Admin kontrolü - sadece belirli email adresine sahip kullanıcı admin"""
    if current_user.email != ADMIN_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this endpoint"
        )
    return current_user


@router.post("/admin/create", response_model=PromoCodeResponse)
async def create_promotion_code(
    request: CreatePromoCodeRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(is_admin)
):
    """
    Admin endpoint: Yeni promosyon kodu oluştur
    Sadece ADMIN_EMAIL sahibi bu endpoint'i kullanabilir
    """
    new_code = PromotionCode.generate_code()
    
    # Aynı kod varsa yeniden oluştur (çok nadir)
    while True:
        result = await db.execute(select(PromotionCode).filter(PromotionCode.code == new_code))
        if not result.scalars().first():
            break
        new_code = PromotionCode.generate_code()

    # Expiry date hesapla
    expires_at = None
    if request.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)

    promo_code = PromotionCode(
        code=new_code,
        description=request.description,
        max_uses=request.max_uses,
        expires_at=expires_at
    )
    
    db.add(promo_code)
    await db.commit()
    await db.refresh(promo_code)
    
    return promo_code

@router.get("/admin/list", response_model=List[PromoCodeResponse])
async def list_promotion_codes(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(is_admin)
):
    """Admin endpoint: Tüm promosyon kodlarını listele"""
    result = await db.execute(select(PromotionCode).order_by(PromotionCode.created_at.desc()))
    codes = result.scalars().all()
    return codes

@router.delete("/admin/{code_id}")
async def delete_promotion_code(
    code_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(is_admin)
):
    """Admin endpoint: Promosyon kodunu sil"""
    result = await db.execute(select(PromotionCode).filter(PromotionCode.id == code_id))
    promo_code = result.scalars().first()
    if not promo_code:
        raise HTTPException(status_code=404, detail="Promotion code not found")
    
    await db.delete(promo_code)
    await db.commit()
    return {"message": "Promotion code deleted successfully"}

@router.patch("/admin/{code_id}/deactivate")
async def deactivate_promotion_code(
    code_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(is_admin)
):
    """Admin endpoint: Promosyon kodunu deaktive et"""
    result = await db.execute(select(PromotionCode).filter(PromotionCode.id == code_id))
    promo_code = result.scalars().first()
    if not promo_code:
        raise HTTPException(status_code=404, detail="Promotion code not found")
    
    promo_code.is_active = False
    await db.commit()
    return {"message": "Promotion code deactivated successfully"}

@router.post("/validate", response_model=ValidatePromoResponse)
async def validate_promotion_code(
    request: ValidatePromoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Kullanıcı endpoint: Promosyon kodunu doğrula ve aktive et
    """
    
    code_to_validate = request.code.upper().strip()
    logger.info(f"Validating promotion code: {code_to_validate} for user: {current_user.email}")

    # Kodu bul
    result = await db.execute(select(PromotionCode).filter(
        PromotionCode.code == code_to_validate
    ))
    promo_code = result.scalars().first()
    
    if not promo_code:
        logger.warning(f"Code '{code_to_validate}' not found in database.")
        return ValidatePromoResponse(
            success=False,
            message="Invalid promotion code"
        )
    
    logger.info(f"Found code: {promo_code.code} (ID: {promo_code.id})")

    # Kod geçerli mi kontrol et
    if not promo_code.is_active:
        logger.warning(f"Code '{promo_code.code}' is not active.")
        return ValidatePromoResponse(
            success=False,
            message="This promotion code is no longer active"
        )
    
    # Kullanım limiti kontrolü
    if promo_code.current_uses >= promo_code.max_uses:
        logger.warning(f"Code '{promo_code.code}' has reached its usage limit ({promo_code.current_uses}/{promo_code.max_uses}).")
        return ValidatePromoResponse(
            success=False,
            message="This promotion code has reached its usage limit"
        )
    
    # Kod expiry kontrolü
    if promo_code.expires_at and promo_code.expires_at < datetime.utcnow():
        logger.warning(f"Code '{promo_code.code}' has expired at {promo_code.expires_at}.")
        return ValidatePromoResponse(
            success=False,
            message="This promotion code has expired"
        )
    
    # Kullanıcı daha önce bu kodu kullanmış mı?
    result = await db.execute(select(UserPromotion).filter(
        and_(
            UserPromotion.user_id == current_user.id,
            UserPromotion.promotion_code_id == promo_code.id
        )
    ))
    existing_promo = result.scalars().first()
    
    if existing_promo:
        logger.warning(f"User '{current_user.email}' has already used code '{promo_code.code}'.")
        return ValidatePromoResponse(
            success=False,
            message="You have already used this promotion code"
        )
    
    # Kullanıcının aktif promosyonu var mı?
    result = await db.execute(select(UserPromotion).filter(
        and_(
            UserPromotion.user_id == current_user.id,
            UserPromotion.is_active == True,
            UserPromotion.expires_at > datetime.utcnow()
        )
    ))
    active_promo = result.scalars().first()
    
    if active_promo:
        logger.warning(f"User '{current_user.email}' already has an active promotion.")
        return ValidatePromoResponse(
            success=False,
            message="You already have an active promotion"
        )
    
    logger.info(f"Code '{promo_code.code}' is valid for user '{current_user.email}'. Activating promotion.")

    # Promosyonu aktive et
    user_promo = UserPromotion(
        user_id=current_user.id,
        promotion_code_id=promo_code.id,
        expires_at=datetime.utcnow() + timedelta(days=7)  # 7 gün unlimited
    )
    
    # Kullanım sayısını artır
    promo_code.current_uses += 1
    
    db.add(user_promo)
    await db.commit()
    
    logger.info(f"Successfully activated promotion for user '{current_user.email}'.")
    
    return ValidatePromoResponse(
        success=True,
        message="Promotion activated successfully! You now have 7 days of unlimited page processing."
    )


@router.get("/admin/users-with-promos")
async def list_users_with_active_promos(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(is_admin)
):
    """Admin endpoint: Aktif promosyonu olan kullanıcıları listele"""
    result = await db.execute(select(UserPromotion).filter(
        and_(
            UserPromotion.is_active == True,
            UserPromotion.expires_at > datetime.utcnow()
        )
    ))
    active_promos = result.scalars().all()
    
    result = []
    for promo in active_promos:
        result.append({
            "user_email": promo.user.email,
            "user_name": promo.user.name,
            "code_used": promo.promotion_code.code,
            "activated_at": promo.activated_at,
            "expires_at": promo.expires_at,
            "days_remaining": promo.days_remaining
        })
    
    return result

@router.post("/cancel")
async def cancel_user_promotion(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Kullanıcı endpoint: Aktif promosyon kodunu iptal et
    """
    logger.info(f"Cancelling promotion for user: {current_user.email}")
    
    # Kullanıcının aktif promosyonunu bul
    result = await db.execute(select(UserPromotion).filter(
        and_(
            UserPromotion.user_id == current_user.id,
            UserPromotion.is_active == True,
            UserPromotion.expires_at > datetime.utcnow()
        )
    ))
    active_promo = result.scalars().first()
    
    if not active_promo:
        logger.warning(f"No active promotion found for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't have an active promotion to cancel"
        )
    
    # Promosyonu iptal et
    active_promo.is_active = False
    await db.commit()
    
    logger.info(f"Successfully cancelled promotion for user: {current_user.email}")
    
    return {"message": "Your promotion has been successfully cancelled"}
