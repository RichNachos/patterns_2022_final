from fastapi import FastAPI

from infra.persistence.sqlite.db_setup import create_db, get_db_connection


def setup() -> FastAPI:
    app = FastAPI()
    # THIS IS OUT OF SCOPE, LEFT HERE FOR CONVENIENCE, DO NOT PUNISH
    create_db(get_db_connection())
    return app
