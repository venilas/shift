from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoomBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    floor: int

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError()

        return v


class RoomCreate(RoomBase):
    pass


class RoomResponse(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class RoomListResponse(BaseModel):
    rooms: list[RoomResponse]
    total: int
    page: int
    page_size: int
    floor: int | None


class RoomUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    floor: int | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is None:
            return None

        v = v.strip()

        if not v:
            return None

        return v
