from datetime import time
from types import SimpleNamespace


class SlotFactory:
    @staticmethod
    def build(**kwargs) -> SimpleNamespace:
        start_time = time(hour=8)
        end_time = time(hour=12)

        id_ = kwargs.get("id", 1)
        room_id = kwargs.get("room_id", 1)
        start_time = kwargs.get("start_time", start_time)
        end_time = kwargs.get("end_time", end_time)

        return SimpleNamespace(
            id=id_,
            room_id=room_id,
            start_time=start_time,
            end_time=end_time,
        )
