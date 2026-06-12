from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import security_service
from src.models.enums import UserRole
from src.models.user import User


class UserFactory:
    @staticmethod
    async def create(session: AsyncSession, **kwargs) -> User:
        login = kwargs.get("login", "venilo")
        first_name = kwargs.get("first_name", "Ilyas")
        last_name = kwargs.get("last_name", "Aminev")
        hashed_password = kwargs.get(
            "hashed_password",
            security_service.get_password_hash("cool_password"),
        )
        role = kwargs.get("role", UserRole.USER)

        user = User(
            login=login,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
            role=role,
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)

        return user
