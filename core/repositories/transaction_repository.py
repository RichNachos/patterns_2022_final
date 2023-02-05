from typing import Protocol

from core.models.transaction import Transaction


class TransactionRepository(Protocol):
    def add_transaction(self, transaction: Transaction) -> None:
        pass

    def get_transactions(self, wallet_address: str) -> list[Transaction]:
        pass

    def get_user_transactions(self, user_token: str) -> list[Transaction]:
        pass

    def get_all_transactions(self) -> list[Transaction]:
        pass
