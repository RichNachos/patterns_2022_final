from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.facade import BitcoinService
from core.interactors.admin_interactor import AdminStatus
from infra.api.fastapi.dependables import get_core


class StatisticsSchema(BaseModel):
    profit: Decimal
    transaction_count: int


admin_api = APIRouter()


@admin_api.get("/statistics", response_model=StatisticsSchema)
async def get_statistics(
    token: str, core: BitcoinService = Depends(get_core)
) -> StatisticsSchema:
    response = core.get_statistics(token)
    match response.status:
        case AdminStatus.UNAUTHORIZED:
            raise HTTPException(
                403, "You have to be an admin to view the platform statistics"
            )
        case AdminStatus.SUCCESS:
            assert response.statistics is not None
            return StatisticsSchema(
                profit=response.statistics.profit,
                transaction_count=response.statistics.transaction_count,
            )
