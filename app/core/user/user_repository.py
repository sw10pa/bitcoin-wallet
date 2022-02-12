from typing import Optional, Protocol

from app.core.entities import UserInfo


class IUserRepository(Protocol):
    def get_user(self, api_key: str) -> Optional[UserInfo]:
        pass

    def get_user_by_email(self, email: str) -> Optional[UserInfo]:
        pass

    def register_user(self, user_info: UserInfo) -> None:
        pass
