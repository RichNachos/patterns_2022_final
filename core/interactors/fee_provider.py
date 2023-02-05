from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


class FeeProvider(Protocol):
    def provide(self, transaction_amount: Decimal) -> Decimal:
        pass


@dataclass
class PercentageFeeProvider:
    fee_ratio: Decimal

    def provide(self, transaction_amount: Decimal) -> Decimal:
        return transaction_amount * self.fee_ratio
