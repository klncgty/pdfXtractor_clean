from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

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

class PDF(Base):
    __tablename__ = 'pdfs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    pdf_filename = Column(String, nullable=False)
    pages_total = Column(Integer, nullable=False)
    pages_processed = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=func.now())
    user = relationship('User', back_populates='pdfs')
