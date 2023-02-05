import unittest.mock
from decimal import Decimal

from core.models.transaction import Transaction
from core.models.user import User
from core.models.wallet import Wallet
from core.repositories.transaction_repository import TransactionRepository
from core.repositories.user_repository import UserRepository
from core.repositories.wallet_repository import WalletRepository


def get_transaction_repo(transactions: list[Transaction]) -> TransactionRepository:
    repo = unittest.mock.Mock()
    repo.get_transactions.return_value = transactions
    repo.get_user_transactions.return_value = transactions
    repo.get_all_transactions.return_value = transactions
    return repo


def get_user_repo(user: User | None) -> UserRepository:
    repo = unittest.mock.Mock()
    repo.get_user.return_value = user
    return repo


def get_wallet_repo(
    create_wallet: bool = True,
    get_wallet_return: Wallet | None = Wallet("test", Decimal(1), "test"),
    get_wallets_by_user_return: list[Wallet] | None = None,
) -> WalletRepository:
    if get_wallets_by_user_return is None:
        get_wallets_by_user_return = list()
    wallet_repo = unittest.mock.Mock()
    wallet_repo.create_wallet.return_value = create_wallet
    wallet_repo.get_wallet.return_value = get_wallet_return
    wallet_repo.get_wallets_by_user.return_value = get_wallets_by_user_return
    return wallet_repo
