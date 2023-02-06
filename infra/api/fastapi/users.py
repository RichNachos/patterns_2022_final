from fastapi import Depends

from core.facade import BitcoinService
from infra.api.fastapi.dependables import get_core, user_api


@user_api.post("/users")
async def register_user(
    username: str, core: BitcoinService = Depends(get_core)
) -> None:
    pass
