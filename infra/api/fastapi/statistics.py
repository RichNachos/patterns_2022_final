from fastapi import Depends

from core.facade import BitcoinService
from infra.api.fastapi.dependables import admin_api, get_core


@admin_api.get("/statistics")
async def get_statistics(token: str, core: BitcoinService = Depends(get_core)) -> None:
    pass
