import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User
from database import AsyncSessionLocal

async def weekly_reset():
    while True:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
            for user in users:
                user.pages_processed_this_month = 0
                user.last_reset_date = datetime.utcnow()
            await db.commit()
        # Haftada bir çalışacak (604800 saniye)
        await asyncio.sleep(604800)
