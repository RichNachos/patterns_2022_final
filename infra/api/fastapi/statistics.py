from fastapi import Depends

from infra.api.fastapi.dependables import BitcoinService, admin_api, get_core


@admin_api.get("/statistics")
async def perform_transaction(
    token: str, core: BitcoinService = Depends(get_core)
) -> None:
    pass
