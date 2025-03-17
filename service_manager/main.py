from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from service_manager.database_structure.models import Base
from service_manager.service.routers import router as api_router
from service_manager.settings import settings

app = FastAPI()


async_engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)


@app.on_event("startup")
async def startup():
    """
    Create tables if they do not exist
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(api_router, prefix="/api")


