from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import secrets
import string
import random

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    monthly_page_limit = Column(Integer, default=30)
    pages_processed_this_month = Column(Integer, default=0)
    last_reset_date = Column(DateTime, default=func.now())
    pdfs = relationship('PDF', back_populates='user')
    api_keys = relationship('APIKey', back_populates='user')
    subscription = relationship('Subscription', back_populates='user', uselist=False)
    user_promotions = relationship('UserPromotion', back_populates='user')

class PDF(Base):
    __tablename__ = 'pdfs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    pdf_filename = Column(String, nullable=False)
    pages_total = Column(Integer, nullable=False)
    pages_processed = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=func.now())
    user = relationship('User', back_populates='pdfs')

class APIKey(Base):
    __tablename__ = 'api_keys'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    api_key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)  # "My App Integration"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_used = Column(DateTime, nullable=True)
    requests_made_this_month = Column(Integer, default=0)
    monthly_request_limit = Column(Integer, default=1000)
    user = relationship('User', back_populates='api_keys')
    
    @classmethod
    def generate_api_key(cls):
        return f"pdfx_{''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32))}"

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    plan_type = Column(String, default='free')  # 'free', 'standard', 'pro'
    status = Column(String, default='inactive')  # 'active', 'inactive', 'cancelled', 'past_due'
    monthly_page_limit = Column(Integer, default=30)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user = relationship('User', back_populates='subscription')

class PromotionCode(Base):
    __tablename__ = 'promotion_codes'
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    max_uses = Column(Integer, default=1)  # How many times this code can be used
    current_uses = Column(Integer, default=0)  # How many times it has been used
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)  # Optional expiry for the code itself
    description = Column(String, nullable=True)  # Admin notes
    user_promotions = relationship('UserPromotion', back_populates='promotion_code')
    
    @classmethod
    def generate_code(cls, length=8):
        """Generate a random promotion code"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @property
    def is_valid(self):
        """Check if code is still valid"""
        if not self.is_active:
            return False
        if self.current_uses >= self.max_uses:
            return False
        if self.expires_at and self.expires_at < func.now():
            return False
        return True

class UserPromotion(Base):
    __tablename__ = 'user_promotions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    promotion_code_id = Column(Integer, ForeignKey('promotion_codes.id'), nullable=False)
    activated_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)  # When the promotion expires for this user
    is_active = Column(Boolean, default=True)
    user = relationship('User', back_populates='user_promotions')
    promotion_code = relationship('PromotionCode', back_populates='user_promotions')
    
    @property
    def days_remaining(self):
        """Calculate days remaining for this promotion"""
        if not self.is_active or not self.expires_at:
            return 0
        from datetime import datetime
        now = datetime.utcnow()
        if self.expires_at <= now:
            return 0
        diff = self.expires_at - now
        return max(0, diff.days + (1 if diff.seconds > 0 else 0))