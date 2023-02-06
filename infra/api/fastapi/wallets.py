from decimal import Decimal
from http.client import HTTPException

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.facade import BitcoinService
from core.interactors.wallet_interactor import WalletInfo, WalletResponse, WalletStatus
from infra.api.fastapi.dependables import get_core

wallet_api = APIRouter()


def handle_wallet_status(status: WalletStatus) -> None:
    match status:
        case WalletStatus.WALLET_NOT_FOUND:
            raise HTTPException(404, "Wallet not found")
        case WalletStatus.UNAUTHORIZED:
            raise HTTPException(403, "Unauthorized")
        case WalletStatus.WALLET_LIMIT_EXCEEDED:
            raise HTTPException(409, "Wallet platform limit exceeded")
        case WalletStatus.FAILED_TO_GET_RATE:
            raise HTTPException(500, "Rate fetch failed")
        case WalletStatus.ERROR:
            raise HTTPException(500, "Error")


class CreateWalletSchema(BaseModel):
    token: str


class WalletSchema(BaseModel):
    address: str
    balance_btc: Decimal
    balance_usd: Decimal


def convert_wallet_info(wallet_info: WalletInfo) -> WalletSchema:
    return WalletSchema(
        address=wallet_info.wallet_address,
        balance_btc=wallet_info.balance_btc,
        balance_usd=wallet_info.balance_usd,
    )


def handle_response(response: WalletResponse) -> WalletSchema:
    handle_wallet_status(response.status)
    if response.value is None:
        raise HTTPException(500, "Unreachable error")
    return convert_wallet_info(response.value)


@wallet_api.post("/wallets", response_model=WalletSchema)
async def create_wallet(
    wallet_data: CreateWalletSchema, core: BitcoinService = Depends(get_core)
) -> WalletSchema:
    return handle_response(core.create_wallet(wallet_data.token))


@wallet_api.get("/wallets/{address}", response_model=WalletSchema)
async def get_wallet(
    token: str, address: str, core: BitcoinService = Depends(get_core)
) -> WalletSchema:
    return handle_response(core.get_wallet(token, address))
