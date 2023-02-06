from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.facade import BitcoinService
from core.interactors.user_interactor import UserStatus
from infra.api.fastapi.dependables import get_core


class UserData(BaseModel):
    username: str


class UserSchema(BaseModel):
    token: str


user_api = APIRouter()


@user_api.post("/users", response_model=UserSchema)
async def register_user(
    user_data: UserData, core: BitcoinService = Depends(get_core)
) -> UserSchema:
    response = core.register_user(user_data.username)
    match response.status:
        case UserStatus.USERNAME_IN_USE:
            raise HTTPException(409, "Username already taken")
        case UserStatus.EXCEPTION:
            raise HTTPException(500, "Unknown error")
        case UserStatus.SUCCESS:
            assert response.user_token is not None
            return UserSchema(token=response.user_token)
