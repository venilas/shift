from datetime import UTC, datetime, timedelta
from types import SimpleNamespace


class BookingFactory:
    @staticmethod
    def build(**kwargs) -> SimpleNamespace:
        today = datetime.now(tz=UTC)

        start_time = today.replace(hour=7, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(minutes=5)

        id_ = kwargs.get("id", 1)
        user_id = kwargs.get("user_id", 1)
        room_id = kwargs.get("room_id", 1)
        start_time = kwargs.get("start_time", start_time)
        end_time = kwargs.get("end_time", end_time)
        description = kwargs.get("description", "Room description")
        start_time
        end_time

        return SimpleNamespace(
            id=id_,
            user_id=user_id,
            room_id=room_id,
            start_time=start_time,
            end_time=end_time,
            description=description,
        )
