from typing import Protocol

from core.models.user import User


class UserRepository(Protocol):
    def create_user(self, user: User) -> bool:
        pass

    def get_user(self, token: str) -> User | None:
        pass

    def username_taken(self, username: str) -> bool:
        pass
