import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .api.auth import AuthAPI
from .factories.user import UserFactory


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    auth = AuthAPI(client)

    response = await auth.register()
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert "access_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_login(client: AsyncClient, db_session: AsyncSession):
    auth = AuthAPI(client)

    user = await UserFactory.create(db_session)

    response = await auth.login(login=user.login)
    data = response.json()

    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_register_duplicate_login(client: AsyncClient, db_session: AsyncSession):
    auth = AuthAPI(client)

    await UserFactory.create(db_session)

    response = await auth.register()
    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert data["detail"] == "Login already registered"


@pytest.mark.asyncio
async def test_register_short_login(client: AsyncClient):
    auth = AuthAPI(client)

    response = await auth.register(login="ven")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at least 5 characters"


@pytest.mark.asyncio
async def test_register_long_login(client: AsyncClient):
    auth = AuthAPI(client)

    response = await auth.register(login="v" * 51)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at most 50 characters"


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    auth = AuthAPI(client)

    response = await auth.register(password="cool")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at least 8 characters"


@pytest.mark.asyncio
async def test_register_long_password(client: AsyncClient):
    auth = AuthAPI(client)

    response = await auth.register(password="c" * 101)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at most 100 characters"


@pytest.mark.asyncio
async def test_register_short_first_name(client: AsyncClient):
    auth = AuthAPI(client)

    response = await auth.register(first_name="Il")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at least 3 characters"


@pytest.mark.asyncio
async def test_register_long_firts_name(client: AsyncClient):
    auth = AuthAPI(client)

    response = await auth.register(first_name="I" * 65)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at most 64 characters"


@pytest.mark.asyncio
async def test_register_short_last_name(client: AsyncClient):
    auth = AuthAPI(client)

    response = await auth.register(last_name="Am")
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at least 3 characters"


@pytest.mark.asyncio
async def test_register_long_last_name(client: AsyncClient):
    auth = AuthAPI(client)

    response = await auth.register(last_name="A" * 65)
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"][0]["msg"] == "String should have at most 64 characters"


@pytest.mark.asyncio
async def test_login_invalid_login(client: AsyncClient, db_session: AsyncSession):
    auth = AuthAPI(client)

    await UserFactory.create(db_session)

    response = await auth.login(login="venilo_o")
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Incorrect login or password"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, db_session: AsyncSession):
    auth = AuthAPI(client)

    await UserFactory.create(db_session)

    response = await auth.login(password="invalid_password")
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Incorrect login or password"


@pytest.mark.asyncio
async def test_login_invalid_creditials(client: AsyncClient):
    auth = AuthAPI(client)

    response = await auth.login()
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Incorrect login or password"
