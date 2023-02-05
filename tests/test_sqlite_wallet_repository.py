import sqlite3
from decimal import Decimal

import pytest

from core.models.wallet import Wallet
from core.repositories.wallet_repository import WalletRepository
from infra.persistence.sqlite.db_setup import create_db
from infra.persistence.sqlite.sqlite_wallet_repository import SqliteWalletRepository


@pytest.fixture
def repo() -> WalletRepository:
    conn = sqlite3.connect(":memory:")
    create_db(conn)

    setup_statements = [
        "INSERT INTO users(token, username) VALUES ('test1', 'test1')",
        "INSERT INTO users(token, username) VALUES ('test2', 'test2')",
    ]

    for statement in setup_statements:
        conn.execute(statement)

    conn.commit()

    return SqliteWalletRepository(conn)


def test_create_wallet_wrong_user(repo: WalletRepository) -> None:
    assert not repo.create_wallet(Wallet("asdasd", Decimal("123"), "wrong"))


def test_create_wallet_success(repo: WalletRepository) -> None:
    assert repo.create_wallet(Wallet("asdasd", Decimal("123"), "test1"))


def test_get_wallet_wrong_address(repo: WalletRepository) -> None:
    assert repo.get_wallet("wrong") is None


def test_get_wallet_correct(repo: WalletRepository) -> None:
    wallet1 = Wallet("test", Decimal("123"), "test1")
    assert repo.create_wallet(Wallet("test", Decimal("123"), "test1"))
    wallet2 = repo.get_wallet("test")
    assert wallet1 == wallet2


def test_update_balance_correct(repo: WalletRepository) -> None:
    wallet = Wallet("test", Decimal("5"), "test1")
    repo.create_wallet(wallet)
    repo.update_wallet_balance_if_exists(wallet.address, Decimal("10"))

    wallet2 = repo.get_wallet(wallet.address)
    assert wallet2 is not None
    assert wallet2.balance == Decimal(10)


def test_get_wallets_by_user_empty(repo: WalletRepository) -> None:
    assert repo.get_wallets_by_user("random") == []


def test_get_wallets_by_user_correct(repo: WalletRepository) -> None:
    wallet1 = Wallet("wallet1", Decimal("123"), "test1")
    wallet2 = Wallet("wallet2", Decimal("111"), "test1")
    repo.create_wallet(wallet1)
    repo.create_wallet(wallet2)

    assert repo.get_wallets_by_user("test1") == [wallet1, wallet2]
