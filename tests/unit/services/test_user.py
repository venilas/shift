import pytest

from src.core.exceptions.user import (
    ForbiddenException,
    LoginAlreadyRegisteredException,
    UserNotFoundException,
)
from src.models.enums import UserRole
from src.schemas.user import UserCreate, UserResponse

from ..factories.user import UserFactory


@pytest.mark.asyncio
async def test_create_user_success(user_repo, user_service):
    user = UserFactory.build()

    user_repo.exists_by_login.return_value = False
    user_repo.create.return_value = user

    result = await user_service.create_user(
        UserCreate(
            login=user.login,
            first_name=user.first_name,
            last_name=user.last_name,
            password="cool_password",
        )
    )

    assert result == UserResponse.model_validate(user)

    user_repo.exists_by_login.assert_called_once_with(user.login)
    user_repo.create.assert_called_once()

    create_data = user_repo.create.call_args.args[0]

    assert create_data["login"] == user.login
    assert create_data["first_name"] == user.first_name
    assert create_data["last_name"] == user.last_name
    assert "hashed_password" in create_data
    assert "password" not in create_data


@pytest.mark.asyncio
async def test_create_user_login_already_registered(user_repo, user_service):
    user = UserFactory.build()

    user_repo.exists_by_login.return_value = True

    with pytest.raises(LoginAlreadyRegisteredException):
        await user_service.create_user(
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
async def test_get_user_by_id_success(user_repo, user_service):
    user = UserFactory.build()

    user_repo.get_by_id.return_value = user

    result = await user_service.get_user_by_id(user_id=user.id)

    assert result == UserResponse.model_validate(user)

    user_repo.get_by_id.assert_called_once_with(user.id)


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_repo, user_service):
    user_repo.get_by_id.return_value = None

    with pytest.raises(UserNotFoundException):
        await user_service.get_user_by_id(user_id=1)

    user_repo.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_user_success(user_repo, user_service):
    user = UserFactory.build()

    user_repo.get_by_id.return_value = user

    await user_service.delete_user(user_id=user.id)

    user_repo.get_by_id.assert_called_once_with(user.id)
    user_repo.delete.assert_called_once_with(user.id)


@pytest.mark.asyncio
async def test_delete_user_not_found(user_repo, user_service):
    user = UserFactory.build()

    user_repo.get_by_id.return_value = None

    with pytest.raises(UserNotFoundException):
        await user_service.delete_user(user_id=user.id)

    user_repo.get_by_id.assert_called_once_with(user.id)
    user_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_user_forbidden(user_repo, user_service):
    user = UserFactory.build(role=UserRole.ADMIN)

    user_repo.get_by_id.return_value = user

    with pytest.raises(ForbiddenException):
        await user_service.delete_user(user_id=user.id)

    user_repo.get_by_id.assert_called_once_with(user.id)
    user_repo.delete.assert_not_called()
