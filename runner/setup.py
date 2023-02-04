import sqlite3

from fastapi import FastAPI

from infra.persistence.sqlite.db_setup import create_db, get_db_connection


def setup() -> FastAPI:
    app = FastAPI()
    create_db(get_db_connection())  # THIS IS OUT OF SCOPE, LEFT HERE FOR CONVENIENCE, DO NOT PUNISH
    return app
