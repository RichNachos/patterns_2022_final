from dataclasses import dataclass
from decimal import Decimal
from sqlite3 import Connection, Cursor

from core.models.transaction import Transaction
from core.repositories.transaction_repository import TransactionRepository


def result_to_list(result: Cursor) -> list[Transaction]:
    data = result.fetchall()
    transaction_list = []
    for row in data:
        transaction_list.append(
            Transaction(row[0], row[1], Decimal(row[2]), Decimal(row[3]))
        )
    return transaction_list


@dataclass
class SqliteTransactionRepository(TransactionRepository):
    conn: Connection

    def add_transaction(self, transaction: Transaction) -> None:
        cursor = self.conn.cursor()
        id1 = self.get_wallet_id(transaction.from_wallet_address)
        id2 = self.get_wallet_id(transaction.to_wallet_address)

        cursor.execute(
            "INSERT INTO transactions (from_wallet_id, to_wallet_id, fee, amount) "
            "VALUES (?,?,?,?)",
            [
                id1,
                id2,
                transaction.fee.__str__(),
                transaction.amount.__str__(),
            ],
        )
        self.conn.commit()

    def get_transactions(self, wallet_address: str) -> list[Transaction]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT wf.address,wt.address,t.fee,t.amount FROM transactions t "
            "JOIN wallets wf ON t.from_wallet_id = wf.id "
            "JOIN wallets wt ON t.to_wallet_id = wt.id "
            "WHERE wf.address = ? OR wt.address = ?",
            [wallet_address, wallet_address],
        )
        return result_to_list(cursor)

    def get_user_transactions(self, user_token: str) -> list[Transaction]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT wf.address, wt.address, t.fee, t.amount FROM transactions t "
            "JOIN wallets wf ON wf.id = t.from_wallet_id "
            "JOIN wallets wt ON wt.id = t.to_wallet_id "
            "JOIN users u ON wt.user_id = u.id OR wf.user_id = u.id "
            "WHERE u.token = (?)",
            (user_token,),
        )

        return result_to_list(cursor)

    def get_all_transactions(self) -> list[Transaction]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT wf.address,wt.address,t.fee,t.amount FROM transactions t "
            "JOIN wallets wf ON t.from_wallet_id = wf.id "
            "JOIN wallets wt ON t.to_wallet_id = wt.id "
        )
        return result_to_list(cursor)

    def get_wallet_id(self, address: str) -> int:
        cursor = self.conn.cursor()
        result = cursor.execute("SELECT * FROM wallets WHERE address = ?", [address])
        data = result.fetchone()
        assert data is not None
        return int(data[0])
