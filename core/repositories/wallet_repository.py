from decimal import Decimal
from typing import Protocol

from core.models.wallet import Wallet


class WalletRepository(Protocol):
    def get_wallet(self, address: str) -> Wallet | None:
        pass

    def update_wallet_balance_if_exists(
        self, wallet_address: str, new_balance: Decimal
    ) -> None:
        pass

    def get_wallets_by_user(self, user_token: str) -> list[Wallet]:
        pass

    def create_wallet(self, wallet: Wallet) -> bool:
        pass
