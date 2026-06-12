from fastapi import Response
from httpx import AsyncClient

from .base import BaseAPIClient


class RoomAPI(BaseAPIClient):
    def __init__(self, client: AsyncClient):
        self.client = client

    async def create(
        self,
        auth_data: dict,
        title: str = "Test Room 1",
        floor: int = 1,
    ) -> Response:
        return await self.client.post(
            "/api/v1/admin/rooms/",
            headers=self._auth_headers(auth_data),
            json={
                "title": title,
                "floor": floor,
            },
        )

    async def update(
        self,
        auth_data: dict | None,
        room_id: int,
        title: str | None = None,
        floor: int | None = None,
    ) -> Response:
        return await self.client.patch(
            f"/api/v1/admin/rooms/{room_id}",
            headers=self._auth_headers(auth_data),
            json=self._build_params(
                title=title,
                floor=floor,
            ),
        )

    async def delete(self, auth_data: dict, room_id: int) -> Response:
        return await self.client.delete(
            f"/api/v1/admin/rooms/{room_id}",
            headers=self._auth_headers(auth_data),
        )

    async def get_multi(
        self,
        auth_data: dict,
        page: int | None = None,
        page_size: int | None = None,
        floor: int | None = None,
    ) -> Response:
        return await self.client.get(
            "/api/v1/rooms/",
            headers=self._auth_headers(auth_data),
            params=self._build_params(
                page=page,
                page_size=page_size,
                floor=floor,
            ),
        )

    async def get_availability(
        self,
        auth_data: dict,
        room_id: int,
        date: str | None = None,
    ) -> Response:

        if date is None:
            date = self._get_msc_date().strftime("%Y-%m-%d")

        return await self.client.get(
            f"/api/v1/rooms/{room_id}/availability",
            headers=self._auth_headers(auth_data),
            params=self._build_params(date=date),
        )
