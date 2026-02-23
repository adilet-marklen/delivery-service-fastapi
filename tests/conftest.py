from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from delivery_service.api.deps import get_db
from delivery_service.db.base import Base
from delivery_service.db.models.parcel import Parcel
from delivery_service.db.models.parcel_type import ParcelType
from delivery_service.main import create_app

TEST_DB_DSN = os.getenv("TEST_DB_DSN") or os.getenv("DELIVERY_DB_DSN")


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    if not TEST_DB_DSN:
        pytest.skip("TEST_DB_DSN/DELIVERY_DB_DSN не задан. Пропускаем интеграционные тесты API.")

    engine = create_async_engine(TEST_DB_DSN, future=True, poolclass=NullPool)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    except Exception as exc:  # pragma: no cover
        await engine.dispose()
        pytest.skip(f"Не удалось подключиться к тестовой БД: {exc!r}")

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def session_factory(
    test_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(loop_scope="session")
async def db_seeded(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[None, None]:
    async with session_factory() as session:
        await session.execute(delete(Parcel))
        await session.execute(delete(ParcelType))
        session.add_all(
            [
                ParcelType(name="clothes"),
                ParcelType(name="electronics"),
                ParcelType(name="other"),
            ]
        )
        await session.commit()
    yield


@pytest_asyncio.fixture(loop_scope="session")
async def parcel_type_ids(
    db_seeded,
    session_factory: async_sessionmaker[AsyncSession],
) -> dict[str, int]:
    async with session_factory() as session:
        rows = await session.execute(select(ParcelType).order_by(ParcelType.name.asc()))
        types = rows.scalars().all()
    return {item.name: item.id for item in types}


@pytest_asyncio.fixture(loop_scope="session")
async def app(session_factory: async_sessionmaker[AsyncSession]):
    app = create_app()

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(loop_scope="session")
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
