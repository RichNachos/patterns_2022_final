import sqlite3
from decimal import Decimal
from sqlite3 import Connection

import pytest

from core.models.transaction import Transaction
from infra.persistence.sqlite.sqlite_transaction_repository import (
    SqliteTransactionRepository,
)


@pytest.fixture
def conn() -> Connection:
    conn = sqlite3.connect(":memory:")
    create_tables = [
        "DROP TABLE IF EXISTS users;"
        "DROP TABLE IF EXISTS wallets;"
        "DROP TABLE IF EXISTS transactions;"
        "CREATE TABLE IF NOT EXISTS users"
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR, token VARCHAR,"
        "UNIQUE (username),"
        "UNIQUE (token))",
        "CREATE TABLE IF NOT EXISTS wallets"
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, address VARCHAR,"
        " user_id INTEGER, balance VARCHAR,"
        "FOREIGN KEY (user_id) REFERENCES users (id),"
        "UNIQUE (address))",
        "CREATE TABLE IF NOT EXISTS transactions"
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, from_wallet_id INTEGER, "
        " to_wallet_id INTEGER, fee VARCHAR, amount VARCHAR, "
        "FOREIGN KEY (from_wallet_id) REFERENCES wallets (id),"
        "FOREIGN KEY (to_wallet_id) REFERENCES wallets (id))",
        "INSERT INTO users (username, token) VALUES ('user1', 'token1');",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address1', 1, 0);",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address2', 1, 0);",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address3', 1, 0);",
        "INSERT INTO wallets (address, user_id, balance) VALUES ('address4', 1, 0);",
    ]
    for statement in create_tables:
        conn.cursor().executescript(statement)
    conn.commit()
    return conn


def test_add_transaction(conn: Connection) -> None:
    repo = SqliteTransactionRepository(conn)
    transaction = Transaction("address1", "address2", Decimal(0.1), Decimal(10))
    repo.add_transaction(transaction)
    assert len(repo.get_all_transactions()) == 1
    assert repo.get_all_transactions()[0].from_wallet_address == "address1"
    assert repo.get_all_transactions()[0].to_wallet_address == "address2"
    assert repo.get_all_transactions()[0].fee == Decimal(0.1)


# This test requires wallet table rows in order to work properly
def test_get_transactions(conn: Connection) -> None:
    repo = SqliteTransactionRepository(conn)

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


def test_get_all_transactions(conn: Connection) -> None:
    repo = SqliteTransactionRepository(conn)

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
