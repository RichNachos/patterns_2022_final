from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Generic, Protocol, TypeVar

from core.interactors.fee_provider import FeeProvider
from core.models.transaction import Transaction
from core.repositories.transaction_repository import TransactionRepository
from core.repositories.user_repository import UserRepository
from core.repositories.wallet_repository import WalletRepository


class TransactionStatus(Enum):
    UNAUTHORIZED = 1
    WALLET_NOT_FOUND = 2
    BALANCE_INSUFFICIENT = 3
    SUCCESS = 4


T = TypeVar("T")


@dataclass
class TransactionResponse(Generic[T]):
    status: TransactionStatus
    value: T


class TransactionInteractor(Protocol):
    def do_transaction(
        self,
        wallet_address_from: str,
        wallet_address_to: str,
        user_token: str,
        amount: Decimal,
    ) -> TransactionResponse[Transaction | None]:
        pass

    def get_transactions(
        self, user_token: str
    ) -> TransactionResponse[list[Transaction]]:
        pass

    def get_transactions_by_wallet(
        self, wallet_address: str, user_token: str
    ) -> TransactionResponse[list[Transaction]]:
        pass


class BitcoinServiceTransactionInteractor:
    def __init__(
        self,
        user_repo: UserRepository,
        wallet_repo: WalletRepository,
        transaction_repo: TransactionRepository,
        fee_provider: FeeProvider,
    ):
        self._user_repo = user_repo
        self._wallet_repo = wallet_repo
        self._transaction_repo = transaction_repo
        self._fee_provider = fee_provider

    def do_transaction(
        self,
        wallet_address_from: str,
        wallet_address_to: str,
        user_token: str,
        amount: Decimal,
    ) -> TransactionResponse[Transaction | None]:
        wallet_from = self._wallet_repo.get_wallet(wallet_address_from)
        wallet_to = self._wallet_repo.get_wallet(wallet_address_to)

        if wallet_from is None or wallet_to is None:
            return TransactionResponse(TransactionStatus.WALLET_NOT_FOUND, None)

        if user_token != wallet_from.owner_token:
            return TransactionResponse(TransactionStatus.UNAUTHORIZED, None)

        fee = (
            self._fee_provider.provide(amount)
            if wallet_from.owner_token != wallet_to.owner_token
            else Decimal(0)
        )

        if wallet_from.balance < fee + amount:
            return TransactionResponse(TransactionStatus.BALANCE_INSUFFICIENT, None)

        self._wallet_repo.update_wallet_balance_if_exists(
            wallet_address_from, wallet_from.balance - fee - amount
        )

        self._wallet_repo.update_wallet_balance_if_exists(
            wallet_address_to, wallet_to.balance + amount
        )

        transaction = Transaction(wallet_address_from, wallet_address_to, fee, amount)

        self._transaction_repo.add_transaction(transaction)

        return TransactionResponse(TransactionStatus.SUCCESS, transaction)

    def get_transactions(
        self, user_token: str
    ) -> TransactionResponse[list[Transaction]]:
        user = self._user_repo.get_user(user_token)

        if user is None:
            return TransactionResponse(TransactionStatus.UNAUTHORIZED, [])

        transactions = self._transaction_repo.get_user_transactions(user_token)

        return TransactionResponse(TransactionStatus.SUCCESS, transactions)

    def get_transactions_by_wallet(
        self, wallet_address: str, user_token: str
    ) -> TransactionResponse[list[Transaction]]:
        wallet = self._wallet_repo.get_wallet(wallet_address)

        if wallet is None:
            return TransactionResponse(TransactionStatus.WALLET_NOT_FOUND, [])

        if wallet.owner_token != user_token:
            return TransactionResponse(TransactionStatus.UNAUTHORIZED, [])

        transactions = self._transaction_repo.get_transactions(wallet_address)

        return TransactionResponse(TransactionStatus.SUCCESS, transactions)
