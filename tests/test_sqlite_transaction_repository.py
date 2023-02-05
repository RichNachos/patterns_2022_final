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
        "INSERT INTO users (username, token) VALUES ('user2', 'token2');"
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address1', 1, 0);",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address2', 1, 0);",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address3', 1, 0);",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address4', 1, 0);",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address5', 2, 0);",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address6', 2, 0);",
    ]
    for statement in insert_rows:
        conn.cursor().executescript(statement)
    conn.commit()
    return SqliteTransactionRepository(conn)


def test_add_transaction(repo: SqliteTransactionRepository) -> None:
    transaction = Transaction("address1", "address2", Decimal(0.1), Decimal(10))
    repo.add_transaction(transaction)
    assert repo.get_all_transactions() == [transaction]


def test_get_transactions(repo: SqliteTransactionRepository) -> None:
    transaction1 = Transaction("address1", "address3", Decimal(0.1), Decimal(10))
    transaction2 = Transaction("address2", "address3", Decimal(0.2), Decimal(10))
    transaction3 = Transaction("address4", "address2", Decimal(0.3), Decimal(10))
    repo.add_transaction(transaction1)
    repo.add_transaction(transaction2)
    repo.add_transaction(transaction3)
    assert repo.get_transactions("address2") == [transaction2, transaction3]


def test_get_user_transactions(repo: SqliteTransactionRepository) -> None:
    transaction1 = Transaction("address1", "address2", Decimal(0.1), Decimal(5))
    transaction2 = Transaction("address1", "address5", Decimal(0.2), Decimal(10))
    transaction3 = Transaction("address5", "address6", Decimal(0.3), Decimal(15))

    repo.add_transaction(transaction1)
    repo.add_transaction(transaction2)
    repo.add_transaction(transaction3)

    res = repo.get_user_transactions("token1")

    assert transaction1 in res
    assert transaction2 in res
    assert transaction3 not in res


def test_get_all_transactions(repo: SqliteTransactionRepository) -> None:
    transaction1 = Transaction("address1", "address2", Decimal(0.1), Decimal(10))
    transaction2 = Transaction("address2", "address3", Decimal(0.2), Decimal(10))
    transaction3 = Transaction("address3", "address4", Decimal(0.3), Decimal(10))
    repo.add_transaction(transaction1)
    repo.add_transaction(transaction2)
    repo.add_transaction(transaction3)
    assert repo.get_all_transactions() == [transaction1, transaction2, transaction3]
