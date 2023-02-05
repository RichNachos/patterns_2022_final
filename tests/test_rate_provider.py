from decimal import Decimal

import pytest

from core.interactors.rate_provider import GeckoRateProvider
import vcr


@pytest.fixture
def provider() -> GeckoRateProvider:
    return GeckoRateProvider(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&precision=full"
    )


@pytest.mark.block_network
def test_failure(provider: GeckoRateProvider) -> None:
    assert provider.fetch() is None
