from datetime import time

from pydantic import BaseModel, ConfigDict, model_validator

from src.core.exceptions.common import (
    InvalidTimeRangeException,
    TimeInvalidIncrementException,
    TimeTooShortException,
)


class SlotCreate(BaseModel):
    room_id: int
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def check_times(self) -> "SlotCreate":
        if self.start_time > self.end_time:
            raise InvalidTimeRangeException()

        start_time_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_time_minutes = self.end_time.hour * 60 + self.end_time.minute

        if end_time_minutes - start_time_minutes < 5:
            raise TimeTooShortException()

        if (end_time_minutes - start_time_minutes) % 5 != 0:
            raise TimeInvalidIncrementException()

        return self


class SlotUpdate(BaseModel):
    room_id: int | None = None
    start_time: time | None = None
    end_time: time | None = None

    @model_validator(mode="after")
    def check_times(self) -> "SlotUpdate":
        if self.start_time and self.end_time:
            start_time_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_time_minutes = self.end_time.hour * 60 + self.end_time.minute

            if end_time_minutes - start_time_minutes < 5:
                raise TimeTooShortException()

            if (end_time_minutes - start_time_minutes) % 5 != 0:
                raise TimeInvalidIncrementException()

        return self


class SlotAvailability(BaseModel):
    start_time: time
    end_time: time


class SlotListAvailability(BaseModel):
    slots: list[SlotAvailability]


class SlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    start_time: time
    end_time: time
