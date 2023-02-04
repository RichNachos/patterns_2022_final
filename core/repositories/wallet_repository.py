from typing import Protocol

from core.models.wallet import Wallet


class WalletRepository(Protocol):
    def get_wallet(self, address: str) -> Wallet | None:
        pass

    def create_wallet(self, user_token: str, wallet: Wallet) -> bool:
        pass
