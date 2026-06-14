import pytest

from src.core.exceptions.user import (
    IncorrectLoginOrPassword,
    LoginAlreadyRegisteredException,
)
from src.schemas.auth import LoginRequest
from src.schemas.user import UserCreate

from ..factories.user import UserFactory


@pytest.mark.asyncio
async def test_register_success(user_repo, auth_service):
    user = UserFactory.build()

    user_repo.exists_by_login.return_value = False
    user_repo.create.return_value = user

    result = await auth_service.register(
        UserCreate(
            login=user.login,
            first_name=user.first_name,
            last_name=user.last_name,
            password="cool_password",
        )
    )

    assert type(result.access_token) is str
    assert result.token_type == "Bearer"

    user_repo.exists_by_login.assert_called_once_with(user.login)
    user_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_login_already_registered(user_repo, auth_service):
    user = UserFactory.build()

    user_repo.exists_by_login.return_value = True

    with pytest.raises(LoginAlreadyRegisteredException):
        await auth_service.register(
            UserCreate(
                login=user.login,
                first_name=user.first_name,
                last_name=user.last_name,
                password="cool_password",
            )
        )

    user_repo.exists_by_login.assert_called_once_with(user.login)
    user_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_login_success(user_repo, auth_service):
    user = UserFactory.build()

    user_repo.get_by_login.return_value = user

    result = await auth_service.login(
        LoginRequest(
            login=user.login,
            password="cool_password",
        )
    )

    assert type(result.access_token) is str
    assert result.token_type == "Bearer"

    user_repo.get_by_login.assert_called_once_with(user.login)


@pytest.mark.asyncio
async def test_login_incorrect_login_or_password(user_repo, auth_service):
    user = UserFactory.build()

    user_repo.get_by_login.return_value = user

    with pytest.raises(IncorrectLoginOrPassword):
        await auth_service.login(
            UserCreate(
                login=user.login,
                first_name=user.first_name,
                last_name=user.last_name,
                password="invalid_password",
            )
        )

    user_repo.get_by_login.assert_called_once_with(user.login)
