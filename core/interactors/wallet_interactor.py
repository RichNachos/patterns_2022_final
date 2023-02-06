from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Protocol

from core.interactors.rate_provider import RateProvider
from core.interactors.tokens import TokenProvider
from core.models.wallet import Wallet
from core.repositories.user_repository import UserRepository
from core.repositories.wallet_repository import WalletRepository


class WalletStatus(Enum):
    WALLET_NOT_FOUND = 0
    UNAUTHORIZED = 1
    WALLET_LIMIT_EXCEEDED = 2
    FAILED_TO_GET_RATE = 4
    ERROR = 5
    SUCCESS = 6


@dataclass
class WalletInfo:
    wallet_address: str
    balance_btc: Decimal
    balance_usd: Decimal


@dataclass
class WalletResponse:
    status: WalletStatus
    value: WalletInfo | None


class WalletInteractor(Protocol):
    def create_wallet(self, user_token: str) -> WalletResponse:
        pass

    def get_wallet(self, wallet_address: str, user_token: str) -> WalletResponse:
        pass


class BitcoinServiceWalletInteractor:
    def __init__(
        self,
        token_provider: TokenProvider,
        user_repo: UserRepository,
        wallet_repo: WalletRepository,
        rate_provider: RateProvider,
        initial_deposit: Decimal,
        max_wallets: int,
    ):
        self._token_provider = token_provider
        self._user_repo = user_repo
        self._wallet_repo = wallet_repo
        self._rate_provider = rate_provider
        self._initial_deposit = initial_deposit
        self._max_wallets = max_wallets

    def _fetch_and_make_wallet_info(self, wallet: Wallet) -> WalletInfo | None:
        rate = self._rate_provider.fetch()
        if rate is None:
            return None
        wallet_info = WalletInfo(wallet.address, wallet.balance, wallet.balance * rate)
        return wallet_info

    def create_wallet(self, user_token: str) -> WalletResponse:
        user = self._user_repo.get_user(user_token)

        if user is None:
            return WalletResponse(WalletStatus.UNAUTHORIZED, None)

        wallets = self._wallet_repo.get_wallets_by_user(user_token)
        if len(wallets) >= self._max_wallets:
            return WalletResponse(WalletStatus.WALLET_LIMIT_EXCEEDED, None)

        new_wallet = Wallet(
            self._token_provider.provide_token(),
            self._initial_deposit,
            user_token,
        )

        wallet_info = self._fetch_and_make_wallet_info(new_wallet)

        if wallet_info is None:
            return WalletResponse(WalletStatus.FAILED_TO_GET_RATE, None)

        if self._wallet_repo.create_wallet(new_wallet):
            return WalletResponse(WalletStatus.SUCCESS, wallet_info)

        return WalletResponse(WalletStatus.ERROR, None)

    def get_wallet(self, wallet_address: str, user_token: str) -> WalletResponse:
        wallet = self._wallet_repo.get_wallet(wallet_address)

        if wallet is None:
            return WalletResponse(WalletStatus.WALLET_NOT_FOUND, None)

        if wallet.owner_token != user_token:
            return WalletResponse(WalletStatus.UNAUTHORIZED, None)

        wallet_info = self._fetch_and_make_wallet_info(wallet)
        if wallet_info is None:
            return WalletResponse(WalletStatus.FAILED_TO_GET_RATE, None)
        return WalletResponse(WalletStatus.SUCCESS, wallet_info)
