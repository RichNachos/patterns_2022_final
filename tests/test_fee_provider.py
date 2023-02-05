from decimal import Decimal

import pytest

from core.interactors.fee_provider import PercentageFeeProvider


@pytest.fixture
def fee_provider() -> PercentageFeeProvider:
    return PercentageFeeProvider(Decimal("0.5"))


def test_provide_fee_normal(fee_provider: PercentageFeeProvider) -> None:
    amount = Decimal("100")

    assert fee_provider.provide(amount) == Decimal("50")


def test_provide_fee_zero(fee_provider: PercentageFeeProvider) -> None:
    amount = Decimal("0")

    assert fee_provider.provide(amount) == Decimal("0")
