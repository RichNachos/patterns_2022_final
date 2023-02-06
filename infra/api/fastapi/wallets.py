from fastapi import Depends

from core.facade import BitcoinService
from infra.api.fastapi.dependables import get_core, user_api


@user_api.post("/wallets")
async def create_wallet(token: str, core: BitcoinService = Depends(get_core)) -> None:
    pass


@user_api.get("/wallets/{address}")
async def get_wallet(
    token: str, address: str, core: BitcoinService = Depends(get_core)
) -> None:
    pass


@user_api.get("/wallets/{address}/transactions")
async def get_wallet_transactions(
    token: str, address: str, core: BitcoinService = Depends(get_core)
) -> None:
    pass
