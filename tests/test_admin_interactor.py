import unittest.mock
from decimal import Decimal

from core.interactors.admin_interactor import (
    AdminStatus,
    BitcoinServiceAdminInteractor,
    Statistics,
)
from core.interactors.tokens import TokenValidator
from core.models.transaction import Transaction
from core.repositories.transaction_repository import TransactionRepository


def get_validator(return_val: bool) -> TokenValidator:
    validator_mock = unittest.mock.Mock()
    validator_mock.validate_token.return_value = return_val
    return validator_mock


def get_transaction_repo(transactions: list[Transaction]) -> TransactionRepository:
    mock = unittest.mock.Mock()
    mock.get_all_transactions.return_value = transactions
    return mock


def test_transaction_service_unauthorized() -> None:
    interactor = BitcoinServiceAdminInteractor(
        get_validator(False), get_transaction_repo([])
    )

    assert interactor.get_statistics("some token").status == AdminStatus.UNAUTHORIZED


def test_transaction_service_authorized_correct_transactions() -> None:
    transactions = [
        Transaction("1", "2", Decimal(2), Decimal(1)),
        Transaction("2", "1", Decimal(3), Decimal(1)),
    ]
    interactor = BitcoinServiceAdminInteractor(
        get_validator(True), get_transaction_repo(transactions)
    )

    ret = interactor.get_statistics("asdasda")
    assert ret.status == AdminStatus.SUCCESS
    assert ret.statistics == Statistics(Decimal(5), 2)
