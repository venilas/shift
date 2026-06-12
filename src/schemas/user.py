from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserBase(BaseModel):
    login: str = Field(min_length=5, max_length=50)

    @field_validator("login")
    @classmethod
    def validate_login(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError()

        return v


class UserCreate(UserBase):
    first_name: str = Field(min_length=3, max_length=64)
    last_name: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=100)

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError()

        return v

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError()

        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError()

        return v


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
