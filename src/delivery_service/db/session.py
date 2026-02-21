from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from delivery_service.core.config import settings

engine = create_async_engine(settings.db_dsn, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
