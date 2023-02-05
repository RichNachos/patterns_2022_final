from decimal import Decimal
from sqlite3 import Connection

from core.models.wallet import Wallet


class SqliteWalletRepository:
    def __init__(self, con: Connection):
        self._con = con

    def get_wallet(self, address: str) -> Wallet | None:
        row = (
            self._con.cursor()
            .execute(
                "SELECT w.balance, u.token  "
                "FROM wallets w join users u on w.user_id = u.id WHERE w.address = ?",
                [address],
            )
            .fetchone()
        )
        if row is None:
            return None

        wallet = Wallet(address, Decimal(row[0]), row[1])

        return wallet

    def get_wallets_by_user(self, user_token: str) -> list[Wallet]:
        wallet_list: list[Wallet] = []
        rows = (
            self._con.cursor()
            .execute(
                "SELECT w.address, w.balance, u.token  "
                "FROM wallets w join users u on w.user_id = u.id WHERE u.token = ?",
                [user_token],
            )
            .fetchall()
        )

        for row in rows:
            wallet_list.append(Wallet(row[0], Decimal(row[1]), row[2]))

        return wallet_list

    def update_wallet_balance_if_exists(
        self, wallet_address: str, new_balance: Decimal
    ) -> None:
        cursor = self._con.cursor()
        cursor.execute(
            "UPDATE wallets set balance = ? where address = ?",
            [str(new_balance), wallet_address],
        )

        self._con.commit()

    def create_wallet(self, wallet: Wallet) -> bool:
        user = (
            self._con.cursor()
            .execute(
                "SELECT id FROM users where token = ?",
                [wallet.owner_token],
            )
            .fetchone()
        )
        if user is None:
            return False

        self._con.cursor().execute(
            "INSERT INTO wallets (address, user_id, balance) VALUES (?, ?, ?)",
            [wallet.address, user[0], str(wallet.balance)],
        )

        self._con.commit()

        return True
