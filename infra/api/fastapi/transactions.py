from fastapi import Depends

from infra.api.fastapi.dependables import BitcoinService, get_core, user_api


@user_api.post("/transactions")
async def perform_transaction(core: BitcoinService = Depends(get_core)) -> None:
    pass


@user_api.get("/transactions")
async def get_transactions(
    token: str, core: BitcoinService = Depends(get_core)
) -> None:
    pass
