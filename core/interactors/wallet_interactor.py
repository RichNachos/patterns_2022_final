from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Generic, Protocol, TypeVar

from core.interactors.fee_provider import FeeProvider
from core.interactors.rate_provider import RateProvider
from core.interactors.tokens import TokenProvider
from core.models.transaction import Transaction
from core.models.wallet import Wallet
from core.repositories.transaction_repository import TransactionRepository
from core.repositories.user_repository import UserRepository
from core.repositories.wallet_repository import WalletRepository


class WalletStatus(Enum):
    WALLET_NOT_FOUND = 0
    UNAUTHORIZED = 1
    WALLET_LIMIT_EXCEEDED = 2
    WALLET_BALANCE_INSUFFICIENT = 3
    FAILED_TO_GET_RATE = 4
    ERROR = 5
    SUCCESS = 6


T = TypeVar("T")


@dataclass
class WalletResponse(Generic[T]):
    status: WalletStatus
    value: T


@dataclass
class WalletInfo:
    wallet_address: str
    balance_btc: Decimal
    balance_usd: Decimal


class WalletInteractor(Protocol):
    def create_wallet(self, user_token: str) -> WalletResponse[WalletInfo | None]:
        pass

    def get_wallet(
        self, wallet_address: str, user_token: str
    ) -> WalletResponse[WalletInfo | None]:
        pass

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


class BitcoinServiceWalletInteractor:
    def __init__(
        self,
        token_provider: TokenProvider,
        transaction_repo: TransactionRepository,
        user_repo: UserRepository,
        wallet_repo: WalletRepository,
        rate_provider: RateProvider,
        fee_provider: FeeProvider,
        initial_deposit: Decimal,
    ):
        self._token_provider = token_provider
        self._transaction_repo = transaction_repo
        self._user_repo = user_repo
        self._wallet_repo = wallet_repo
        self._rate_provider = rate_provider
        self._fee_provider = fee_provider
        self._initial_deposit = initial_deposit

    def create_wallet(self, user_token: str) -> WalletResponse[WalletInfo | None]:
        user = self._user_repo.get_user(user_token)

        if user is None:
            return WalletResponse(WalletStatus.UNAUTHORIZED, None)

        wallets = self._wallet_repo.get_wallets_by_user(user_token)
        if len(wallets) >= 3:
            return WalletResponse(WalletStatus.WALLET_LIMIT_EXCEEDED, None)

        rate = self._rate_provider.fetch()
        if rate is None:
            return WalletResponse(WalletStatus.FAILED_TO_GET_RATE, None)

        new_wallet = Wallet(
            self._token_provider.provide_token(),
            self._initial_deposit,
            user_token,
        )

        if self._wallet_repo.create_wallet(new_wallet):
            wallet_info = WalletInfo(
                new_wallet.address, new_wallet.balance, new_wallet.balance * rate
            )
            return WalletResponse(WalletStatus.SUCCESS, wallet_info)

        return WalletResponse(WalletStatus.ERROR, None)

    def get_wallet(
        self, wallet_address: str, user_token: str
    ) -> WalletResponse[WalletInfo | None]:

        wallet = self._wallet_repo.get_wallet(wallet_address)

        if wallet is None:
            return WalletResponse(WalletStatus.WALLET_NOT_FOUND, None)

        if wallet.owner_token != user_token:
            return WalletResponse(WalletStatus.UNAUTHORIZED, None)

        rate = self._rate_provider.fetch()
        if rate is None:
            return WalletResponse(WalletStatus.FAILED_TO_GET_RATE, None)

        wallet_info = WalletInfo(wallet.address, wallet.balance, rate * wallet.balance)
        return WalletResponse(WalletStatus.SUCCESS, wallet_info)

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
