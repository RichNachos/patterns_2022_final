from dataclasses import dataclass
from typing import Protocol


@dataclass
class User(Protocol):
    username: str
    token: str
