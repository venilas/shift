from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_in: dict) -> User:
        user = User(**user_in)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_by_login(self, login: str) -> User | None:
        query = select(User).where(func.lower(User.login) == login.lower())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def exists_by_login(self, login: str) -> bool:
        user = await self.get_by_login(login)
        return user is not None

    async def get_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, user_id: int) -> None:
        query = delete(User).where(User.id == user_id)
        await self.session.execute(query)
