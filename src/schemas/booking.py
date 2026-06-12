from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.config.settings import get_settings
from src.core.exceptions.common import (
    CrossDayBookingException,
    InvalidTimeRangeException,
    TimeInvalidIncrementException,
    TimeTooShortException,
)


class BookingCreate(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime
    description: str | None = Field(default=None, min_length=1, max_length=200)

    @field_validator("description")
    @classmethod
    def strip_description(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def check_times(self) -> "BookingCreate":
        self.start_time = self.start_time.replace(second=0)
        self.end_time = self.end_time.replace(second=0)

        if self.start_time > self.end_time:
            raise InvalidTimeRangeException()

        if self.start_time.date() != self.end_time.date():
            raise CrossDayBookingException()

        if (self.end_time - self.start_time).seconds < 5 * 60:
            raise TimeTooShortException()

        if (self.end_time - self.start_time).seconds / 60 % 5 != 0:
            raise TimeInvalidIncrementException()

        tz = ZoneInfo(key=get_settings().TIMEZONE)

        self.start_time = self.start_time.replace(tzinfo=tz)
        self.end_time = self.end_time.replace(tzinfo=tz)

        return self


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    description: str | None

    @model_validator(mode="after")
    def replace_msc_tz(self) -> "BookingResponse":
        tz = ZoneInfo(key=get_settings().TIMEZONE)

        self.start_time = self.start_time.astimezone(tz=tz)
        self.end_time = self.end_time.astimezone(tz=tz)

        return self


class BookingListResponse(BaseModel):
    bookings: list[BookingResponse]


class BookingUpdate(BaseModel):
    room_id: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    description: str | None = Field(default=None, min_length=1, max_length=200)

    @model_validator(mode="after")
    def check_times(self) -> "BookingUpdate":
        if self.start_time and self.end_time:
            if self.start_time > self.end_time:
                raise InvalidTimeRangeException()

            if self.start_time.date() != self.end_time.date():
                raise CrossDayBookingException()

            if (self.end_time - self.start_time).seconds < 5 * 60:
                raise TimeTooShortException()

            if (self.end_time - self.start_time).seconds / 60 % 5 != 0:
                raise TimeInvalidIncrementException()

        return self

    @model_validator(mode="after")
    def replace_msc_tz(self) -> "BookingUpdate":
        tz = ZoneInfo(key=get_settings().TIMEZONE)

        if self.start_time:
            self.start_time = self.start_time.replace(second=0, tzinfo=tz)

        if self.end_time:
            self.end_time = self.end_time.replace(second=0, tzinfo=tz)

        return self
