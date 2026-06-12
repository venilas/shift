from fastapi import Response
from httpx import AsyncClient

from .base import BaseAPIClient


class SlotAPI(BaseAPIClient):
    def __init__(self, client: AsyncClient):
        self.client = client

    async def create(
        self,
        auth_data: dict,
        room_id: int,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> Response:
        if start_time is None:
            start_time = "08:00"
        if end_time is None:
            end_time = "12:00"

        return await self.client.post(
            "/api/v1/admin/slots/",
            headers=self._auth_headers(auth_data),
            json=self._build_params(
                room_id=room_id,
                start_time=start_time,
                end_time=end_time,
            ),
        )

    async def update(
        self,
        auth_data: dict,
        slot_id: int,
        room_id: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> Response:
        return await self.client.patch(
            f"/api/v1/admin/slots/{slot_id}",
            headers=self._auth_headers(auth_data),
            json=self._build_params(
                room_id=room_id,
                start_time=start_time,
                end_time=end_time,
            ),
        )

    async def delete(
        self,
        auth_data: dict,
        slot_id: int,
    ) -> Response:
        return await self.client.delete(
            f"/api/v1/admin/slots/{slot_id}",
            headers=self._auth_headers(auth_data),
        )
