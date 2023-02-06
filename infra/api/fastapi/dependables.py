from fastapi import APIRouter
from starlette.requests import Request

from core.facade import BitcoinService

user_api = APIRouter()
admin_api = APIRouter()


def get_core(request: Request) -> BitcoinService:
    service: BitcoinService = request.app.state.core
    return service
