from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Protocol


class AdminStatus(Enum):
    UNAUTHORIZED = 0
    SUCCESS = 1


@dataclass
class Statistics:
    profit: Decimal
    transaction_count: int


@dataclass
class AdminResponse:
    status: AdminStatus
    statistics: Statistics


class AdminInteractor(Protocol):
    def get_statistics(self, admin_token: str) -> AdminResponse:
        pass
