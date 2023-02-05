from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Wallet:
    address: str
    balance: Decimal
    owner_token: str
