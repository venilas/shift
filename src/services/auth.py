from fastapi import HTTPException, status

from src.core.security import security_service
from src.db.repositories.user import UserRepository
from src.schemas.auth import LoginRequest, Token
from src.schemas.user import UserCreate, UserResponse
from src.services.user import UserService


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, user_in: UserCreate) -> Token:
        user_service = UserService(self.user_repo)
        user = await user_service.create_user(user_in)
        return self._create_token(user)

    async def login(self, login_data: LoginRequest) -> Token:
        user = await self.user_repo.get_by_login(login_data.login)
        if not user or not security_service.verify_password(
            login_data.password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
            )

        return self._create_token(UserResponse.model_validate(user))

    @staticmethod
    def _create_token(user: UserResponse) -> Token:
        return Token(access_token=security_service.create_access_token(str(user.id)))
