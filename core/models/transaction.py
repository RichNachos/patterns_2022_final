from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Transaction:
    from_wallet_address: str
    to_wallet_address: str
    fee: Decimal
    amount: Decimal
