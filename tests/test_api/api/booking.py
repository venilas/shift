from datetime import datetime

from fastapi import Response
from httpx import AsyncClient

from .base import BaseAPIClient


class BookingAPI(BaseAPIClient):
    def __init__(self, client: AsyncClient):
        self.client = client

    async def create(
        self,
        auth_data: dict,
        room_id: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        description: str | None = "Test Description",
    ) -> Response:
        date = self._get_msc_date()
        if start_time is None:
            start_time = self._get_time(date, hour=8, minute=0)
        if end_time is None:
            end_time = self._get_time(date, hour=8, minute=10)

        return await self.client.post(
            "/api/v1/bookings/",
            headers=self._auth_headers(auth_data),
            json=self._build_params(
                room_id=room_id,
                start_time=self._strftime_datetime(start_time),
                end_time=self._strftime_datetime(end_time),
                description=description,
            ),
        )

    async def get_multi(
        self,
        auth_data: dict,
        room_id: int | None = None,
        user_id: int | None = None,
        date: str | None = None,
    ) -> Response:
        return await self.client.get(
            "/api/v1/admin/bookings/",
            headers=self._auth_headers(auth_data),
            params=self._build_params(
                room_id=room_id,
                user_id=user_id,
                date=date,
            ),
        )

    async def update(
        self,
        auth_data: dict,
        booking_id: int,
        room_id: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        description: str | None = None,
    ) -> Response:
        if start_time:
            start_time = self._strftime_datetime(start_time)
        if end_time:
            end_time = self._strftime_datetime(end_time)

        return await self.client.patch(
            f"/api/v1/admin/bookings/{booking_id}",
            headers=self._auth_headers(auth_data),
            json=self._build_params(
                room_id=room_id,
                start_time=start_time,
                end_time=end_time,
                description=description,
            ),
        )

    async def delete(self, auth_data: dict, booking_id: int) -> Response:
        return await self.client.delete(
            f"/api/v1/admin/bookings/{booking_id}",
            headers=self._auth_headers(auth_data),
        )

    async def get_multi_user(
        self,
        auth_data: dict,
        room_id: int | None = None,
    ) -> Response:
        return await self.client.get(
            "/api/v1/bookings/",
            headers=self._auth_headers(auth_data),
            params=self._build_params(room_id=room_id),
        )

    async def update_user(
        self,
        auth_data: dict,
        booking_id: int,
        room_id: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        description: str | None = None,
    ) -> Response:
        if start_time:
            start_time = self._strftime_datetime(start_time)
        if end_time:
            end_time = self._strftime_datetime(end_time)

        return await self.client.patch(
            f"/api/v1/bookings/{booking_id}",
            headers=self._auth_headers(auth_data),
            json=self._build_params(
                room_id=room_id,
                start_time=start_time,
                end_time=end_time,
                description=description,
            ),
        )

    async def delete_user(self, auth_data: dict, booking_id: int) -> Response:
        return await self.client.delete(
            f"/api/v1/bookings/{booking_id}",
            headers=self._auth_headers(auth_data),
        )
