from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from core.interactors.tokens import TokenProvider
from core.models.user import User
from core.repositories.user_repository import UserRepository


class UserStatus(Enum):
    SUCCESS = 0
    USERNAME_IN_USE = 1
    EXCEPTION = 2


@dataclass
class UserResponse:
    status: UserStatus
    user_token: str | None


class UserInteractor(Protocol):
    def create_user(self, username: str) -> UserResponse:
        pass


@dataclass
class BitcoinServiceUserInteractor:
    repo: UserRepository
    token_provider: TokenProvider

    def create_user(self, username: str) -> UserResponse:
        if self.repo.username_taken(username):
            return UserResponse(UserStatus.USERNAME_IN_USE, None)

        token = self.token_provider.provide_token()
        response = self.repo.create_user(User(username, token))
        if response is not True:
            return UserResponse(UserStatus.EXCEPTION, None)

        return UserResponse(UserStatus.SUCCESS, token)
