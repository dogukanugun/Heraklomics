# backend/app/db/init_db.py

import asyncio
from app.core.database import engine, Base
from app.db import models

async def init():
    print("Creating DB tables...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("DB tables created.")

if __name__ == "__main__":
    asyncio.run(init())
