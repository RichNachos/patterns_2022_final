from decimal import Decimal
from http.client import HTTPException

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.facade import BitcoinService
from core.interactors.transaction_interactor import TransactionStatus
from core.models.transaction import Transaction
from infra.api.fastapi.dependables import get_core

transaction_api = APIRouter()


class TransactionSchema(BaseModel):
    from_wallet: str
    to_wallet: str
    fee: Decimal
    amount: Decimal


class TransactionsViewSchema(BaseModel):
    transactions: list[TransactionSchema]


class TransactionRequestSchema(BaseModel):
    token: str
    from_wallet: str
    to_wallet: str
    amount: Decimal


def handle_transaction_status(status: TransactionStatus) -> None:
    match status:
        case TransactionStatus.WALLET_NOT_FOUND:
            raise HTTPException(404, "Wallet not found")
        case TransactionStatus.UNAUTHORIZED:
            raise HTTPException(403, "Unauthorized")
        case TransactionStatus.BALANCE_INSUFFICIENT:
            raise HTTPException(
                409, "Wallet balance insufficient to perform the transaction"
            )


def convert_transaction(transaction: Transaction) -> TransactionSchema:
    return TransactionSchema(
        from_wallet=transaction.from_wallet_address,
        to_wallet=transaction.to_wallet_address,
        fee=transaction.fee,
        amount=transaction.amount,
    )


@transaction_api.get(
    "/wallets/{address}/transactions", response_model=TransactionsViewSchema
)
async def get_wallet_transactions(
    token: str, address: str, core: BitcoinService = Depends(get_core)
) -> TransactionsViewSchema:
    response = core.get_wallet_transactions(token, address)
    handle_transaction_status(response.status)
    return TransactionsViewSchema(
        transactions=[
            convert_transaction(transaction) for transaction in response.value
        ]
    )


@transaction_api.post("/transactions", response_model=TransactionSchema)
async def perform_transaction(
    request: TransactionRequestSchema,
    core: BitcoinService = Depends(get_core),
) -> TransactionSchema:
    response = core.perform_transaction(
        request.token, request.from_wallet, request.to_wallet, request.amount
    )
    handle_transaction_status(response.status)
    if response.value is None:
        raise HTTPException(500, "Unreachable Error")
    return convert_transaction(response.value)


@transaction_api.get("/transactions", response_model=TransactionsViewSchema)
async def get_transactions(
    token: str, core: BitcoinService = Depends(get_core)
) -> TransactionsViewSchema:
    response = core.get_transactions(token)
    handle_transaction_status(response.status)
    return TransactionsViewSchema(
        transactions=[
            convert_transaction(transaction) for transaction in response.value
        ]
    )
