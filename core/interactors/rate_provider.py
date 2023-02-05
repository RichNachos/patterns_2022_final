from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

import requests


class RateProvider(Protocol):
    def fetch(self) -> Decimal | None:
        pass


@dataclass
class GeckoRateProvider:
    url: str

    def fetch(self) -> Decimal | None:
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                data = response.json()
                rate = data["bitcoin"]["usd"]
                if rate is None:
                    return None

                return Decimal(rate)
            return None

        except RuntimeError:
            return None
