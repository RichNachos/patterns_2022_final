from fastapi import Depends

from core.facade import BitcoinService
from infra.api.fastapi.dependables import get_core, user_api


@user_api.post("/transactions")
async def perform_transaction(core: BitcoinService = Depends(get_core)) -> None:
    pass


@user_api.get("/transactions")
async def get_transactions(
    token: str, core: BitcoinService = Depends(get_core)
) -> None:
    pass
