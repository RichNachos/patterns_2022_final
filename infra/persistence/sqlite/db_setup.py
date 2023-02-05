import sqlite3
from sqlite3 import Connection


def get_db_connection() -> Connection:
    return sqlite3.connect("app.db", check_same_thread=False)


def create_db(con: Connection) -> None:
    create_tables = [
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
    ]
    for statement in create_tables:
        con.cursor().execute(statement)
