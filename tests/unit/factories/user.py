from types import SimpleNamespace

from src.core.security import security_service
from src.models.enums import UserRole


class UserFactory:
    @staticmethod
    def build(**kwargs) -> SimpleNamespace:
        id_ = kwargs.get("id", 1)
        login = kwargs.get("login", "venilo")
        first_name = kwargs.get("first_name", "Ilyas")
        last_name = kwargs.get("last_name", "Aminev")
        role = kwargs.get("role", UserRole.USER)
        hashed_password = kwargs.get(
            "hashed_password",
            security_service.get_password_hash("cool_password"),
        )

        return SimpleNamespace(
            id=id_,
            login=login,
            first_name=first_name,
            last_name=last_name,
            role=role,
            hashed_password=hashed_password,
        )
