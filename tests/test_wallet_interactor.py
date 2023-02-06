import unittest.mock
from decimal import Decimal

from core.interactors.rate_provider import RateProvider
from core.interactors.tokens import TokenProvider
from core.interactors.wallet_interactor import (
    BitcoinServiceWalletInteractor,
    WalletInfo,
    WalletInteractor,
    WalletResponse,
    WalletStatus,
)
from core.models.user import User
from core.repositories.user_repository import UserRepository
from core.repositories.wallet_repository import WalletRepository
from tests.mock_repo import get_user_repo, get_wallet_repo


def get_token_provider(token: str) -> TokenProvider:
    provider = unittest.mock.Mock()
    provider.provide_token.return_value = token
    return provider


def get_rate_provider(rate: Decimal | None) -> RateProvider:
    provider = unittest.mock.Mock()
    provider.fetch.return_value = rate
    return provider


def get_wallet_interactor(
    token_provider: TokenProvider = get_token_provider("test"),
    user_repo: UserRepository = get_user_repo(User("test", "test")),
    wallet_repo: WalletRepository = get_wallet_repo(),
    rate_provider: RateProvider = get_rate_provider(Decimal("12.3")),
    initial_deposit: Decimal = Decimal(1),
    max_wallets: int = 3,
) -> WalletInteractor:
    return BitcoinServiceWalletInteractor(
        token_provider=token_provider,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        rate_provider=rate_provider,
        initial_deposit=initial_deposit,
        max_wallets=max_wallets,
    )


def test_create_wallet_basic() -> None:
    wallet_interactor = get_wallet_interactor()

    result = wallet_interactor.create_wallet("test")
    expected_info = WalletInfo("test", Decimal(1), Decimal("12.3"))

    assert result == WalletResponse(WalletStatus.SUCCESS, expected_info)


def test_create_wallet_non_existent_user() -> None:
    wallet_interactor = get_wallet_interactor(user_repo=get_user_repo(None))

    result = wallet_interactor.create_wallet("abc")

    assert result.status == WalletStatus.UNAUTHORIZED
    assert result.value is None


def test_create_wallet_rate_get_failed() -> None:
    wallet_interactor = get_wallet_interactor(rate_provider=get_rate_provider(None))

    result = wallet_interactor.create_wallet("abc")
    assert result.status == WalletStatus.FAILED_TO_GET_RATE
    assert result.value is None


def test_create_wallet_repo_error() -> None:
    wallet_interactor = get_wallet_interactor(
        wallet_repo=get_wallet_repo(create_wallet=False)
    )

    result = wallet_interactor.create_wallet("efg")
    assert result.status == WalletStatus.ERROR
    assert result.value is None


def test_create_wallet_limit_exceeded() -> None:
    wallet_interactor = get_wallet_interactor(max_wallets=0)

    result = wallet_interactor.create_wallet("efg")
    assert result.status == WalletStatus.WALLET_LIMIT_EXCEEDED
    assert result.value is None


def test_get_wallet_basic() -> None:
    wallet_interactor = get_wallet_interactor()

    result = wallet_interactor.get_wallet("test", "test")
    assert result == WalletResponse(
        WalletStatus.SUCCESS, WalletInfo("test", Decimal("1"), Decimal("12.3"))
    )


def test_get_wallet_non_existent_wallet() -> None:
    wallet_interactor = get_wallet_interactor(
        wallet_repo=get_wallet_repo(get_wallet_return=None)
    )

    result = wallet_interactor.get_wallet("test", "test")
    assert result.status == WalletStatus.WALLET_NOT_FOUND


def test_get_wallet_unauthorized() -> None:
    wallet_interactor = get_wallet_interactor()

    result = wallet_interactor.get_wallet("test", "wrong token")
    assert result.status == WalletStatus.UNAUTHORIZED


def test_get_wallet_rate_get_failed() -> None:
    wallet_interactor = get_wallet_interactor(rate_provider=get_rate_provider(None))

    result = wallet_interactor.get_wallet("test", "test")
    assert result.status == WalletStatus.FAILED_TO_GET_RATE
