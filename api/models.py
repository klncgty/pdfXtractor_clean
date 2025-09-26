from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class SubscriptionTier(enum.Enum):
    FREE = "free"
    STANDARD = "standard"
    PRO = "pro"

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    INCOMPLETE = "incomplete"

class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plans'
    id = Column(Integer, primary_key=True, index=True)
    tier = Column(SQLEnum(SubscriptionTier), nullable=False)
    stripe_price_id = Column(String, nullable=False)
    page_limit = Column(Integer, nullable=False)
    price_usd = Column(Integer, nullable=False)  # in cents
    created_at = Column(DateTime, default=func.now())

class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_id = Column(Integer, ForeignKey('subscription_plans.id'), nullable=False)
    stripe_subscription_id = Column(String, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.INCOMPLETE)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    user = relationship('User', back_populates='subscription')
    plan = relationship('SubscriptionPlan')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    monthly_page_limit = Column(Integer, default=30)
    pages_processed_this_month = Column(Integer, default=0)
    last_reset_date = Column(DateTime, default=func.now())
    subscription = relationship('UserSubscription', back_populates='user', uselist=False)
    pdfs = relationship('PDF', back_populates='user')

class PDF(Base):
    __tablename__ = 'pdfs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    pdf_filename = Column(String, nullable=False)
    pages_total = Column(Integer, nullable=False)
    pages_processed = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=func.now())
    user = relationship('User', back_populates='pdfs')
