from datetime import datetime
from zoneinfo import ZoneInfo

from src.config.settings import get_settings
from src.core.security import security_service


class BaseFactory:
    @staticmethod
    def _get_msc_tz() -> ZoneInfo:
        return ZoneInfo(key=get_settings().TIMEZONE)

    @staticmethod
    def _get_msc_datetime() -> datetime:
        tz = BaseFactory._get_msc_tz()
        return datetime.now(tz=tz)

    @staticmethod
    def _response_strftime_time(date_in: datetime) -> str:
        tz = BaseFactory._get_msc_tz()
        return date_in.astimezone(tz=tz).strftime("%Y-%m-%dT%H:%M:%S+03:00")

    @staticmethod
    def _get_user_id(auth_data: dict) -> int:
        token = auth_data["access_token"]
        user = security_service.decode_token(token)
        return int(user["sub"])
