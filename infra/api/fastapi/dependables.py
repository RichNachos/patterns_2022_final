from fastapi import APIRouter
from starlette.requests import Request

user_api = APIRouter()
admin_api = APIRouter()


# Boilerplate
class BitcoinService:
    pass


def get_core(request: Request) -> BitcoinService:
    assert isinstance(request.app.state.core, BitcoinService)
    return request.app.state.core
