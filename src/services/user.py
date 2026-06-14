from src.core.exceptions.user import (
    ForbiddenException,
    LoginAlreadyRegisteredException,
    UserNotFoundException,
)
from src.core.security import security_service
from src.db.repositories.user import UserRepository
from src.models.enums import UserRole
from src.schemas.user import UserCreate, UserResponse


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, user_in: UserCreate) -> UserResponse:
        if await self.user_repo.exists_by_login(user_in.login):
            raise LoginAlreadyRegisteredException()

        user_data = user_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = security_service.get_password_hash(
            user_in.password
        )
        user = await self.user_repo.create(user_data)

        return UserResponse.model_validate(user)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        if user.role == UserRole.ADMIN:
            raise ForbiddenException("Forbidden delete an admin")

        await self.user_repo.delete(user_id)
