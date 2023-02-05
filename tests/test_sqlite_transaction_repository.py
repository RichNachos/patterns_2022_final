import sqlite3
from decimal import Decimal

import pytest

from core.models.transaction import Transaction
from infra.persistence.sqlite.db_setup import create_db
from infra.persistence.sqlite.sqlite_transaction_repository import (
    SqliteTransactionRepository,
)


@pytest.fixture
def repo() -> SqliteTransactionRepository:
    conn = sqlite3.connect(":memory:")
    create_db(conn)
    insert_rows = [
        "INSERT INTO users (username, token) VALUES ('user1', 'token1');",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address1', 1, 0);",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address2', 1, 0);",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address3', 1, 0);",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address4', 1, 0);",
    ]
    for statement in insert_rows:
        conn.cursor().executescript(statement)
    conn.commit()
    return SqliteTransactionRepository(conn)


def test_add_transaction(repo: SqliteTransactionRepository) -> None:
    transaction = Transaction("address1", "address2", Decimal(0.1), Decimal(10))
    repo.add_transaction(transaction)
    assert len(repo.get_all_transactions()) == 1
    assert repo.get_all_transactions()[0].from_wallet_address == "address1"
    assert repo.get_all_transactions()[0].to_wallet_address == "address2"
    assert repo.get_all_transactions()[0].fee == Decimal(0.1)


# This test requires wallet table rows in order to work properly
def test_get_transactions(repo: SqliteTransactionRepository) -> None:
    transaction1 = Transaction("address1", "address2", Decimal(0.1), Decimal(10))
    transaction2 = Transaction("address2", "address3", Decimal(0.2), Decimal(10))
    transaction3 = Transaction("address3", "address4", Decimal(0.3), Decimal(10))
    repo.add_transaction(transaction1)
    repo.add_transaction(transaction2)
    repo.add_transaction(transaction3)
    assert len(repo.get_transactions("address2")) == 2
    assert repo.get_transactions("address2")[0].from_wallet_address == "address1"
    assert repo.get_transactions("address2")[0].to_wallet_address == "address2"
    assert repo.get_transactions("address2")[0].fee == Decimal(0.1)
    assert repo.get_transactions("address2")[1].from_wallet_address == "address2"
    assert repo.get_transactions("address2")[1].to_wallet_address == "address3"
    assert repo.get_transactions("address2")[1].fee == Decimal(0.2)


def test_get_all_transactions(repo: SqliteTransactionRepository) -> None:
    transaction1 = Transaction("address1", "address2", Decimal(0.1), Decimal(10))
    transaction2 = Transaction("address2", "address3", Decimal(0.2), Decimal(10))
    transaction3 = Transaction("address3", "address4", Decimal(0.3), Decimal(10))
    repo.add_transaction(transaction1)
    repo.add_transaction(transaction2)
    repo.add_transaction(transaction3)
    assert len(repo.get_all_transactions()) == 3
    assert repo.get_all_transactions()[0].from_wallet_address == "address1"
    assert repo.get_all_transactions()[0].to_wallet_address == "address2"
    assert repo.get_all_transactions()[0].fee == Decimal(0.1)
    assert repo.get_all_transactions()[1].from_wallet_address == "address2"
    assert repo.get_all_transactions()[1].to_wallet_address == "address3"
    assert repo.get_all_transactions()[1].fee == Decimal(0.2)
    assert repo.get_all_transactions()[2].from_wallet_address == "address3"
    assert repo.get_all_transactions()[2].to_wallet_address == "address4"
    assert repo.get_all_transactions()[2].fee == Decimal(0.3)
