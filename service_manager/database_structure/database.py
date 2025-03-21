from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from service_manager.database_structure.models import Base
from service_manager.settings import settings

async_engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with SessionLocal() as session:
        yield session


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
