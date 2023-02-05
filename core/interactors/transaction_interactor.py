from decimal import Decimal
from typing import Protocol

from core.interactors.fee_provider import FeeProvider
from core.interactors.wallet_interactor import WalletResponse, WalletStatus
from core.models.transaction import Transaction
from core.repositories.transaction_repository import TransactionRepository
from core.repositories.user_repository import UserRepository
from core.repositories.wallet_repository import WalletRepository


class TransactionInteractor(Protocol):
    def do_transaction(
            self,
            wallet_address_from: str,
            wallet_address_to: str,
            user_token: str,
            amount: Decimal,
    ) -> WalletResponse[Transaction | None]:
        pass

    def get_transactions(
            self, user_token: str
    ) -> WalletResponse[list[Transaction] | None]:
        pass

    def get_transactions_by_wallet(
            self, wallet_address: str, user_token: str
    ) -> WalletResponse[list[Transaction] | None]:
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
    ) -> WalletResponse[Transaction | None]:
        wallet_from = self._wallet_repo.get_wallet(wallet_address_from)
        wallet_to = self._wallet_repo.get_wallet(wallet_address_to)

        if wallet_from is None or wallet_to is None:
            return WalletResponse(WalletStatus.WALLET_NOT_FOUND, None)

        if user_token != wallet_from.owner_token:
            return WalletResponse(WalletStatus.UNAUTHORIZED, None)

        fee = self._fee_provider.provide(amount)

        if wallet_from.balance < fee + amount:
            return WalletResponse(WalletStatus.WALLET_BALANCE_INSUFFICIENT, None)

        self._wallet_repo.update_wallet_balance_if_exists(
            wallet_address_from, wallet_from.balance - fee - amount
        )

        self._wallet_repo.update_wallet_balance_if_exists(
            wallet_address_to, wallet_to.balance + amount
        )

        transaction = Transaction(wallet_address_from, wallet_address_to, fee, amount)

        self._transaction_repo.add_transaction(transaction)

        return WalletResponse(WalletStatus.SUCCESS, transaction)

    def get_transactions(self, user_token: str) -> WalletResponse[list[Transaction]]:
        user = self._user_repo.get_user(user_token)

        if user is None:
            return WalletResponse(WalletStatus.UNAUTHORIZED, None)

        transactions = self._transaction_repo.get_user_transactions(user_token)

        return WalletResponse(WalletStatus.SUCCESS, transactions)

    def get_transactions_by_wallet(
        self, wallet_address: str, user_token: str
    ) -> WalletResponse[list[Transaction]]:
        wallet = self._wallet_repo.get_wallet(wallet_address)

        if wallet is None:
            return WalletResponse(WalletStatus.WALLET_NOT_FOUND, None)

        if wallet.owner_token != user_token:
            return WalletResponse(WalletStatus.UNAUTHORIZED, None)

        transactions = self._transaction_repo.get_transactions(wallet_address)

        return WalletResponse(WalletStatus.SUCCESS, transactions)
