from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Generic, Protocol, TypeVar

from core.models.transaction import Transaction
from core.models.wallet import Wallet


class WalletStatus(Enum):
    WALLET_NOT_FOUND = 0
    UNAUTHORIZED = 1
    WALLET_LIMIT_EXCEEDED = 2
    WALLET_BALANCE_INSUFFICIENT = 3
    SUCCESS = 4


T = TypeVar("T")


@dataclass
class WalletResponse(Generic[T]):
    status: WalletStatus
    value: T


class WalletInteractor(Protocol):
    def create_wallet(self, user_token: str) -> WalletResponse[Wallet]:
        pass

    def get_wallet(
        self, wallet_address: str, user_token: str
    ) -> WalletResponse[Wallet]:
        pass

    def do_transaction(
        self,
        wallet_address_from: str,
        wallet_address_to: str,
        user_token: str,
        amount: Decimal,
    ) -> WalletResponse[Transaction]:
        pass

    def get_transactions(self, user_token: str) -> WalletResponse[list[Transaction]]:
        pass

    def get_transactions_by_wallet(
        self, wallet_address: str, user_token: str
    ) -> WalletResponse[list[Transaction]]:
        pass
