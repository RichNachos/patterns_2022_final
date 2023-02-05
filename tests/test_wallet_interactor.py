import unittest.mock
from decimal import Decimal

import pytest

from core.interactors.fee_provider import FeeProvider
from core.interactors.rate_provider import RateProvider
from core.interactors.tokens import TokenProvider
from core.interactors.wallet_interactor import (
    BitcoinServiceWalletInteractor,
    WalletInfo,
    WalletResponse,
    WalletStatus,
)
from core.models.transaction import Transaction
from core.models.user import User
from core.models.wallet import Wallet
from core.repositories.transaction_repository import TransactionRepository
from core.repositories.user_repository import UserRepository
from core.repositories.wallet_repository import WalletRepository


def get_token_provider(token: str) -> TokenProvider:
    provider = unittest.mock.Mock()
    provider.provide_token.return_value = token
    return provider


def get_transaction_repo(transactions: list[Transaction]) -> TransactionRepository:
    repo = unittest.mock.Mock()
    repo.get_transactions.return_value = transactions
    repo.get_user_transactions.return_value = transactions
    repo.get_all_transactions.return_value = transactions
    return repo


def get_user_repo(user: User | None) -> UserRepository:
    repo = unittest.mock.Mock()
    repo.get_user.return_value = user
    return repo


def get_rate_provider(rate: Decimal | None) -> RateProvider:
    provider = unittest.mock.Mock()
    provider.fetch.return_value = rate
    return provider


def get_fee_provider(fee: Decimal) -> FeeProvider:
    provider = unittest.mock.Mock()
    provider.provide.return_value = fee
    return provider


@pytest.fixture
def basic_wallet_repo() -> WalletRepository:
    repo = unittest.mock.Mock()
    repo.create_wallet.return_value = True
    repo.get_wallets_by_user.return_value = []
    return repo


def test_create_wallet_basic(basic_wallet_repo: WalletRepository) -> None:

    wallet_interactor = BitcoinServiceWalletInteractor(
        token_provider=get_token_provider("abc"),
        transaction_repo=get_transaction_repo([]),
        user_repo=get_user_repo(User("abc", "abc")),
        wallet_repo=basic_wallet_repo,
        rate_provider=get_rate_provider(Decimal("15.5")),
        fee_provider=get_fee_provider(Decimal("1.0")),
        initial_deposit=Decimal("1.0"),
    )

    result = wallet_interactor.create_wallet("abc")
    expected_info = WalletInfo("abc", Decimal("1.0"), Decimal("15.5"))

    assert result == WalletResponse(WalletStatus.SUCCESS, expected_info)


def test_create_wallet_non_existent_user(basic_wallet_repo: WalletRepository) -> None:

    wallet_interactor = BitcoinServiceWalletInteractor(
        token_provider=get_token_provider("abc"),
        transaction_repo=get_transaction_repo([]),
        user_repo=get_user_repo(None),
        wallet_repo=basic_wallet_repo,
        rate_provider=get_rate_provider(Decimal("15.5")),
        fee_provider=get_fee_provider(Decimal("1.0")),
        initial_deposit=Decimal("1.0"),
    )

    result = wallet_interactor.create_wallet("abc")

    assert result.status == WalletStatus.UNAUTHORIZED
    assert result.value is None


def test_create_wallet_rate_get_failed(basic_wallet_repo: WalletRepository) -> None:

    wallet_interactor = BitcoinServiceWalletInteractor(
        token_provider=get_token_provider("abc"),
        transaction_repo=get_transaction_repo([]),
        user_repo=get_user_repo(User("abc", "abc")),
        wallet_repo=basic_wallet_repo,
        rate_provider=get_rate_provider(None),
        fee_provider=get_fee_provider(Decimal("1.0")),
        initial_deposit=Decimal("1.0"),
    )

    result = wallet_interactor.create_wallet("abc")
    assert result.status == WalletStatus.FAILED_TO_GET_RATE
    assert result.value is None


def test_create_wallet_repo_error() -> None:

    wallet_repo = unittest.mock.Mock()
    wallet_repo.get_wallets_by_user.return_value = []
    wallet_repo.create_wallet.return_value = False

    wallet_interactor = BitcoinServiceWalletInteractor(
        token_provider=get_token_provider("efg"),
        transaction_repo=get_transaction_repo([]),
        user_repo=get_user_repo(User("efg", "efg")),
        wallet_repo=wallet_repo,
        rate_provider=get_rate_provider(None),
        fee_provider=get_fee_provider(Decimal("1.0")),
        initial_deposit=Decimal("1.0"),
    )

    result = wallet_interactor.create_wallet("abc")
    assert result.status == WalletStatus.ERROR
    assert result.value is None


def test_get_wallet_basic() -> None:

    wallet_repo = unittest.mock.Mock()
    wallet_repo.get_wallet.return_value = Wallet("123", Decimal("1.2"), "abc")

    wallet_interactor = BitcoinServiceWalletInteractor(
        token_provider=get_token_provider("efg"),
        transaction_repo=get_transaction_repo([]),
        user_repo=get_user_repo(User("efg", "efg")),
        wallet_repo=wallet_repo,
        rate_provider=get_rate_provider(None),
        fee_provider=get_fee_provider(Decimal("1.0")),
        initial_deposit=Decimal("1.0"),
    )

    result = wallet_interactor.create_wallet("abc")
    assert result.status == WalletStatus.ERROR
    assert result.value is None


def test_get_wallet_non_existent_wallet() -> None:
    pass


def test_get_wallet_user_doesnt_exist() -> None:
    pass


def test_get_wallet_user_doesnt_match() -> None:
    pass


def test_get_wallet_rate_get_failed() -> None:
    pass


def test_do_transaction_basic() -> None:
    pass


def test_do_transaction_wallet_from_non_existent() -> None:
    pass


def test_do_transaction_wallet_to_non_existent() -> None:
    pass


def test_do_transaction_user_token_wrong() -> None:
    pass


def test_get_transactions_basic() -> None:
    pass


def test_get_transactions_user_non_existent() -> None:
    pass


def test_get_transactions_by_wallet_basic() -> None:
    pass


def test_get_transactions_by_wallet_wallet_non_existent() -> None:
    pass


def test_get_transactions_by_wallet_user_token_wrong() -> None:
    pass
