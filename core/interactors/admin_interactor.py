from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Protocol

from core.interactors.tokens import TokenValidator
from core.repositories.transaction_repository import TransactionRepository


class AdminStatus(Enum):
    UNAUTHORIZED = 0
    SUCCESS = 1


@dataclass
class Statistics:
    profit: Decimal = Decimal("0")
    transaction_count: int = 0


@dataclass
class AdminResponse:
    status: AdminStatus
    statistics: Statistics | None


class AdminInteractor(Protocol):
    def get_statistics(self, admin_token: str) -> AdminResponse:
        pass


class BitcoinServiceAdminInteractor:
    def __init__(
        self, token_validator: TokenValidator, transaction_repo: TransactionRepository
    ):
        self._token_validator = token_validator
        self._transaction_repo = transaction_repo

    def get_statistics(self, admin_token: str) -> AdminResponse:
        if not self._token_validator.validate_token(admin_token):
            return AdminResponse(AdminStatus.UNAUTHORIZED, None)

        stats = Statistics()

        for transaction in self._transaction_repo.get_all_transactions():
            stats.transaction_count += 1
            stats.profit += transaction.fee

        return AdminResponse(AdminStatus.SUCCESS, stats)
