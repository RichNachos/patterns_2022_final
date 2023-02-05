import unittest.mock
from decimal import Decimal

from core.interactors.fee_provider import FeeProvider
from core.interactors.transaction_interactor import (
    BitcoinServiceTransactionInteractor,
    TransactionInteractor,
    TransactionResponse,
    TransactionStatus,
)
from core.models.transaction import Transaction
from core.models.user import User
from core.models.wallet import Wallet
from core.repositories.transaction_repository import TransactionRepository
from core.repositories.user_repository import UserRepository
from core.repositories.wallet_repository import WalletRepository
from tests.mock_repo import get_transaction_repo, get_user_repo, get_wallet_repo


def get_fee_provider(fee: Decimal) -> FeeProvider:
    provider = unittest.mock.Mock()
    provider.provide.return_value = fee
    return provider


def get_transaction_interactor(
    transaction_repo: TransactionRepository = get_transaction_repo(
        [Transaction("test1", "test2", Decimal(1), Decimal(10))]
    ),
    user_repo: UserRepository = get_user_repo(User("test", "test")),
    wallet_repo: WalletRepository = get_wallet_repo(),
    fee_provider: FeeProvider = get_fee_provider(Decimal("0.1")),
) -> TransactionInteractor:
    return BitcoinServiceTransactionInteractor(
        transaction_repo=transaction_repo,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        fee_provider=fee_provider,
    )


def get_wallet(address: str) -> Wallet | None:
    wallet_map = {
        "test1": Wallet("test1", Decimal("1.0"), "test"),
        "test2": Wallet("test2", Decimal("1.0"), "test2"),
        "test3": Wallet("test3", Decimal("0"), "test"),
    }
    if address in wallet_map:
        return wallet_map[address]
    return None


def test_do_transaction_different_owner() -> None:
    wallet_repo = get_wallet_repo()
    wallet_repo.__setattr__("get_wallet", get_wallet)
    interactor = get_transaction_interactor(wallet_repo=wallet_repo)
    transaction = interactor.do_transaction("test1", "test2", "test", Decimal("0.1"))
    assert transaction == TransactionResponse(
        TransactionStatus.SUCCESS,
        Transaction("test1", "test2", Decimal("0.1"), Decimal("0.1")),
    )


def test_do_transaction_same_owner_no_fee() -> None:
    wallet_repo = get_wallet_repo()
    wallet_repo.__setattr__("get_wallet", get_wallet)
    interactor = get_transaction_interactor(wallet_repo=wallet_repo)
    transaction = interactor.do_transaction("test1", "test3", "test", Decimal("0.1"))
    assert transaction == TransactionResponse(
        TransactionStatus.SUCCESS,
        Transaction("test1", "test3", Decimal("0"), Decimal("0.1")),
    )


def test_do_transaction_wallet_from_non_existent() -> None:
    wallet_repo = get_wallet_repo()
    wallet_repo.__setattr__("get_wallet", get_wallet)
    interactor = get_transaction_interactor(wallet_repo=wallet_repo)
    transaction = interactor.do_transaction("WRONG", "test3", "test", Decimal("0.1"))
    assert transaction.status == TransactionStatus.WALLET_NOT_FOUND


def test_do_transaction_wallet_to_non_existent() -> None:
    wallet_repo = get_wallet_repo()
    wallet_repo.__setattr__("get_wallet", get_wallet)
    interactor = get_transaction_interactor(wallet_repo=wallet_repo)
    transaction = interactor.do_transaction("test1", "WRONG", "test", Decimal("0.1"))
    assert transaction.status == TransactionStatus.WALLET_NOT_FOUND


def test_do_transaction_user_token_wrong() -> None:
    wallet_repo = get_wallet_repo()
    wallet_repo.__setattr__("get_wallet", get_wallet)
    interactor = get_transaction_interactor(wallet_repo=wallet_repo)
    transaction = interactor.do_transaction("test1", "test2", "WRONG", Decimal("0.1"))
    assert transaction.status == TransactionStatus.UNAUTHORIZED


def test_get_transactions_basic() -> None:
    interactor = get_transaction_interactor()
    transactions = interactor.get_transactions("test")
    assert transactions == TransactionResponse(
        TransactionStatus.SUCCESS,
        [Transaction("test1", "test2", Decimal(1), Decimal(10))],
    )


def test_get_transactions_user_non_existent() -> None:
    interactor = get_transaction_interactor(user_repo=get_user_repo(None))
    transactions = interactor.get_transactions("test")
    assert transactions.status == TransactionStatus.UNAUTHORIZED


def test_get_transactions_by_wallet_basic() -> None:
    interactor = get_transaction_interactor()
    transactions = interactor.get_transactions_by_wallet("test", "test")
    assert transactions == TransactionResponse(
        TransactionStatus.SUCCESS,
        [Transaction("test1", "test2", Decimal(1), Decimal(10))],
    )


def test_get_transactions_by_wallet_wallet_non_existent() -> None:
    interactor = get_transaction_interactor(
        wallet_repo=get_wallet_repo(get_wallet_return=None)
    )
    transactions = interactor.get_transactions_by_wallet("test", "test")
    assert transactions.status == TransactionStatus.WALLET_NOT_FOUND


def test_get_transactions_by_wallet_user_non_existent() -> None:
    interactor = get_transaction_interactor()
    transactions = interactor.get_transactions_by_wallet("test", "WRONG")
    assert transactions.status == TransactionStatus.UNAUTHORIZED
