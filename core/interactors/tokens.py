import secrets
from typing import Protocol


class TokenValidator(Protocol):
    def validate_token(self, token: str) -> bool:
        pass


class TokenProvider(Protocol):
    def provide_token(self) -> str:
        pass


class RandomHexTokenProvider:
    def __init__(self, token_len_bytes: int):
        self._token_len = token_len_bytes

    def provide_token(self) -> str:
        return secrets.token_hex(self._token_len)


class HardCodedTokenValidator:
    def __init__(self, token: str):
        self._token = token

    def validate_token(self, token: str) -> bool:
        return token == self._token
