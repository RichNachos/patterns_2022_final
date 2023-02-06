from decimal import Decimal

from fastapi import FastAPI

from core.facade import AwesomeBitcoinService
from core.interactors.admin_interactor import BitcoinServiceAdminInteractor
from core.interactors.fee_provider import PercentageFeeProvider
from core.interactors.rate_provider import GeckoRateProvider
from core.interactors.tokens import HardCodedTokenValidator, RandomHexTokenProvider
from core.interactors.transaction_interactor import BitcoinServiceTransactionInteractor
from core.interactors.user_interactor import BitcoinServiceUserInteractor
from core.interactors.wallet_interactor import BitcoinServiceWalletInteractor
from infra.api.fastapi.statistics import admin_api
from infra.api.fastapi.transactions import transaction_api
from infra.api.fastapi.users import user_api
from infra.api.fastapi.wallets import wallet_api
from infra.persistence.sqlite.db_setup import create_db, get_db_connection
from infra.persistence.sqlite.sqlite_transaction_repository import (
    SqliteTransactionRepository,
)
from infra.persistence.sqlite.sqlite_user_repository import SqliteUserRepository
from infra.persistence.sqlite.sqlite_wallet_repository import SqliteWalletRepository

RATE_PROVIDER_URL: str = (
    "https://api.coingecko.com"
    "/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&precision=full"
)
TOKEN_LENGTH_BYTES: int = 32
MAX_WALLETS: int = 3
INITIAL_DEPOSIT: Decimal = Decimal(1)
FEE_PERCENTAGE: Decimal = Decimal("0.015")
ADMIN_TOKEN: str = "12345678"


def setup() -> FastAPI:
    app = FastAPI()
    app.include_router(user_api)
    app.include_router(admin_api)
    app.include_router(wallet_api)
    app.include_router(transaction_api)

    con = get_db_connection()
    # THIS IS OUT OF SCOPE, LEFT HERE FOR CONVENIENCE, DO NOT PUNISH
    create_db(con)

    user_repo = SqliteUserRepository(con)
    wallet_repo = SqliteWalletRepository(con)
    transaction_repo = SqliteTransactionRepository(con)
    token_provider = RandomHexTokenProvider(TOKEN_LENGTH_BYTES)
    rate_provider = GeckoRateProvider(RATE_PROVIDER_URL)
    fee_provider = PercentageFeeProvider(FEE_PERCENTAGE)
    admin_token_validator = HardCodedTokenValidator(ADMIN_TOKEN)
    app.state.core = AwesomeBitcoinService(
        BitcoinServiceUserInteractor(user_repo, token_provider),
        BitcoinServiceWalletInteractor(
            token_provider,
            user_repo,
            wallet_repo,
            rate_provider,
            INITIAL_DEPOSIT,
            MAX_WALLETS,
        ),
        BitcoinServiceTransactionInteractor(
            user_repo, wallet_repo, transaction_repo, fee_provider
        ),
        BitcoinServiceAdminInteractor(admin_token_validator, transaction_repo),
    )

    return app
