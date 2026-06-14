from datetime import datetime, time
from zoneinfo import ZoneInfo

from src.config.settings import get_settings


class BaseAPIClient:
    def _auth_headers(self, auth_data: dict | None) -> dict | None:
        if auth_data:
            token = auth_data["access_token"]
            return {"Authorization": f"Bearer {token}"}
        return None

    def _build_params(self, **kwargs) -> dict:
        return {k: v for k, v in kwargs.items() if v is not None}

    def _get_msc_tz(self) -> ZoneInfo:
        return ZoneInfo(key=get_settings().TIMEZONE)

    def _get_msc_date(self) -> datetime:
        tz = self._get_msc_tz()
        return datetime.now(tz=tz)

    def _strftime_datetime(self, date_in: datetime) -> str:
        tz = self._get_msc_tz()
        return date_in.astimezone(tz=tz).strftime("%Y-%m-%d %H:%M")

    def _strftime_time(self, date_in: time) -> str:
        return date_in.strftime("%H:%M")

    def _get_time(self, date_in: datetime, hour: int, minute: int) -> datetime:
        return date_in.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0,
        )
