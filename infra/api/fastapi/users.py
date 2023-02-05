from fastapi import Depends

from infra.api.fastapi.dependables import BitcoinService, get_core, user_api


@user_api.post("/users")
async def register_user(
    username: str, core: BitcoinService = Depends(get_core)
) -> None:
    pass
