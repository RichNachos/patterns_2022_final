from decimal import Decimal

import pytest

from core.interactors.rate_provider import GeckoRateProvider


@pytest.fixture
def provider() -> GeckoRateProvider:
    return GeckoRateProvider(
        "https://api.coingecko.com"
        "/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&precision=full"
    )


@pytest.mark.block_network
def test_failure(provider: GeckoRateProvider) -> None:
    assert provider.fetch() is None


@pytest.fixture()
def vcr_config() -> dict[str, str]:
    return {
        "record_mode": "new_episodes",
    }


@pytest.mark.vcr()
def test_rate(provider: GeckoRateProvider) -> None:
    assert provider.fetch() == Decimal("22882.95047526271446258760988712310791015625")
