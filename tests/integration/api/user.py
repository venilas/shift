from fastapi import Response
from httpx import AsyncClient

from .base import BaseAPIClient


class UserAPI(BaseAPIClient):
    def __init__(self, client: AsyncClient):
        self.client = client

    async def get(self, auth_data: dict, user_id: int) -> Response:
        return await self.client.get(
            f"/api/v1/admin/users/{user_id}",
            headers=self._auth_headers(auth_data),
        )

    async def delete(self, auth_data: dict, user_id: int) -> Response:
        return await self.client.delete(
            f"/api/v1/admin/users/{user_id}",
            headers=self._auth_headers(auth_data),
        )
