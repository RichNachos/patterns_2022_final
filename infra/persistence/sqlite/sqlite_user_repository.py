import sqlite3
from dataclasses import dataclass
from sqlite3 import Connection

from core.models.user import User


@dataclass
class SqliteUserRepository:
    conn: Connection

    def create_user(self, user: User) -> bool:
        cursor = self.conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, token) VALUES (?, ?)",
                (
                    user.username,
                    user.token,
                ),
            )
            self.conn.commit()
            return True
        # If unique constraint is violated
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False

    def get_user(self, token: str) -> User | None:
        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM users WHERE users.token = (?)", (token,))
        row = cursor.fetchone()

        if row is None:
            return None

        return User(row[1], row[2])

    def username_taken(self, username: str) -> bool:
        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM users WHERE users.username = (?)", (username,))
        row = cursor.fetchall()
        if len(row) == 0:
            return False
        return True
