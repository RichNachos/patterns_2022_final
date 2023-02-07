from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from core.interactors.admin_interactor import AdminInteractor, AdminResponse
from core.interactors.transaction_interactor import (
    TransactionInteractor,
    TransactionResponse,
)
from core.interactors.user_interactor import UserInteractor, UserResponse
from core.interactors.wallet_interactor import WalletInteractor, WalletResponse
from core.models.transaction import Transaction


class BitcoinService(Protocol):
    def register_user(self, username: str) -> UserResponse:
        pass

    def create_wallet(self, token: str) -> WalletResponse:
        pass

    def get_wallet(self, token: str, address: str) -> WalletResponse:
        pass

    def perform_transaction(
        self, token: str, from_address: str, to_address: str, amount: Decimal
    ) -> TransactionResponse[Transaction | None]:
        pass

    def get_transactions(self, token: str) -> TransactionResponse[list[Transaction]]:
        pass

    def get_wallet_transactions(
        self, token: str, address: str
    ) -> TransactionResponse[list[Transaction]]:
        pass

    def get_statistics(self, token: str) -> AdminResponse:
        pass


@dataclass
class AwesomeBitcoinService:
    user_interactor: UserInteractor
    wallet_interactor: WalletInteractor
    transaction_interactor: TransactionInteractor
    admin_interactor: AdminInteractor

    def register_user(self, username: str) -> UserResponse:
        return self.user_interactor.create_user(username)

    def create_wallet(self, token: str) -> WalletResponse:
        return self.wallet_interactor.create_wallet(token)

    def get_wallet(self, token: str, address: str) -> WalletResponse:
        return self.wallet_interactor.get_wallet(address, token)

    def perform_transaction(
        self, token: str, from_address: str, to_address: str, amount: Decimal
    ) -> TransactionResponse[Transaction | None]:
        return self.transaction_interactor.do_transaction(
            from_address, to_address, token, amount
        )

    def get_transactions(self, token: str) -> TransactionResponse[list[Transaction]]:
        return self.transaction_interactor.get_transactions(token)

    def get_wallet_transactions(
        self, token: str, address: str
    ) -> TransactionResponse[list[Transaction]]:
        return self.transaction_interactor.get_transactions_by_wallet(address, token)

    def get_statistics(self, token: str) -> AdminResponse:
        return self.admin_interactor.get_statistics(token)
