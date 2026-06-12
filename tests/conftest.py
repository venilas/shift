from typing import AsyncGenerator

import pytest
import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alembic import command
from src.config.settings import get_settings
from src.db.session import get_db
from src.main import app
from src.models.enums import UserRole

from .test_api.api.auth import AuthAPI
from .test_api.factories.user import UserFactory

TEST_DATABASE_URL = get_settings().DATABASE_URL


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    config = Config("alembic.ini")

    command.upgrade(config, "head")

    yield

    command.downgrade(config, "base")


@pytest_asyncio.fixture(scope="function")
async def session_maker(test_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(scope="function")
async def db_session(
    test_engine,
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.connect() as conn:
        transaction = await conn.begin()

        session = session_maker(bind=conn)

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_data_admin(client: AsyncClient, db_session: AsyncSession) -> dict:
    await UserFactory.create(db_session, role=UserRole.ADMIN)
    auth = AuthAPI(client)
    response = await auth.login()
    return response.json()


@pytest_asyncio.fixture(scope="function")
async def auth_data_user(client: AsyncClient, db_session: AsyncSession) -> dict:
    await UserFactory.create(db_session, login="venilo_o")
    auth = AuthAPI(client)
    response = await auth.login(login="venilo_o")
    return response.json()
