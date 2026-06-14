from types import SimpleNamespace


class RoomFactory:
    @staticmethod
    def build(**kwargs) -> SimpleNamespace:
        id_ = kwargs.get("id", 1)
        title = kwargs.get("title", "Room title")
        floor = kwargs.get("floor", 1)

        return SimpleNamespace(
            id=id_,
            title=title,
            floor=floor,
        )
