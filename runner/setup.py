import sqlite3

from fastapi import FastAPI

DB_NAME = "bitcoin_db"


def setup() -> FastAPI:
    app = FastAPI()
    con = sqlite3.connect(DB_NAME)

    return app
