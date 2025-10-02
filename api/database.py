
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import os
import logging
from typing import AsyncGenerator

from models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment or use SQLite as default
# To use PostgreSQL, set DATABASE_URL environment variable to:
# postgresql+asyncpg://username:password@localhost/dbname
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./octro.db')

# Configure async engine for SQLite
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv('SQL_ECHO', 'False').lower() == 'true',
    future=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {}
)

# Configure session factory with AsyncSession
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async DB session.

    FastAPI expects dependency functions that are async generators (yield). Using
    @asynccontextmanager returns a context manager object which FastAPI will
    not automatically enter; that caused the `_AsyncGeneratorContextManager`
    error. Implementing as an async generator yields the session directly.
    """
    session: AsyncSession = AsyncSessionLocal()
    try:
        logger.debug("Creating new database session")
        yield session
        await session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()

async def check_db_connection() -> bool:
    """Check if the database is reachable"""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

async def create_all_tables():
    """Create all database tables if they don't exist"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

# Test the database connection when this module is imported
if __name__ == "__main__":
    import asyncio
    
    async def test_connection():
        is_connected = await check_db_connection()
        print(f"Database connection successful: {is_connected}")
        
        # Create tables if they don't exist
        if is_connected:
            await create_all_tables()
    
    asyncio.run(test_connection())
