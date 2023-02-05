from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Generic, Protocol, TypeVar

from core.interactors.rate_provider import RateProvider
from core.interactors.tokens import TokenProvider
from core.models.wallet import Wallet
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


class BitcoinServiceWalletInteractor:
    def __init__(
        self,
        token_provider: TokenProvider,
        user_repo: UserRepository,
        wallet_repo: WalletRepository,
        rate_provider: RateProvider,
        initial_deposit: Decimal,
    ):
        self._token_provider = token_provider
        self._user_repo = user_repo
        self._wallet_repo = wallet_repo
        self._rate_provider = rate_provider
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
