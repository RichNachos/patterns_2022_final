from starlette.requests import Request

from core.facade import BitcoinService


def get_core(request: Request) -> BitcoinService:
    service: BitcoinService = request.app.state.core
    return service
