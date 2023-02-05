from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class UserStatus(Enum):
    SUCCESS = 0
    USERNAME_IN_USE = 1


@dataclass
class UserResponse:
    status: UserStatus
    user_token: str


class UserInteractor(Protocol):
    def create_user(self, username: str) -> UserResponse:
        pass
