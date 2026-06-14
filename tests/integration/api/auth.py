from fastapi import Response
from httpx import AsyncClient


class AuthAPI:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def register(
        self,
        login: str = "venilo",
        first_name: str = "Ilyas",
        last_name: str = "Aminev",
        password: str = "cool_password",
    ) -> Response:
        return await self.client.post(
            "/api/v1/auth/register",
            json={
                "login": login,
                "first_name": first_name,
                "last_name": last_name,
                "password": password,
            },
        )

    async def login(
        self,
        login: str = "venilo",
        password: str = "cool_password",
    ) -> Response:
        return await self.client.post(
            "/api/v1/auth/login",
            json={
                "login": login,
                "password": password,
            },
        )
