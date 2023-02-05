import sqlite3

import pytest

from core.models.user import User
from core.repositories.user_repository import UserRepository
from infra.persistence.sqlite.db_setup import create_db
from infra.persistence.sqlite.sqlite_user_repository import SqliteUserRepository


@pytest.fixture
def user_repo() -> UserRepository:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    create_db(conn)
    return SqliteUserRepository(conn)


def test_basic_create_user(user_repo: UserRepository) -> None:
    test_user = User("abc", "efg")

    assert user_repo.create_user(test_user) is True


def test_basic_select_user(user_repo: UserRepository) -> None:
    test_user = User("abc", "efg")

    assert user_repo.create_user(test_user) is True

    returned_user = user_repo.get_user(test_user.token)

    assert returned_user is not None
    assert returned_user.token == test_user.token
    assert returned_user.username == test_user.username


def test_select_non_existent_user(user_repo: UserRepository) -> None:
    assert user_repo.get_user("abc") is None


def test_create_user_with_duplicate_username(user_repo: UserRepository) -> None:
    test_user1 = User("abc", "efg")
    test_user2 = User("abc", "hij")

    assert user_repo.create_user(test_user1) is True
    assert user_repo.create_user(test_user2) is False


def test_create_user_with_duplicate_token(user_repo: UserRepository) -> None:
    test_user1 = User("abc", "efg")
    test_user2 = User("123", "efg")

    assert user_repo.create_user(test_user1) is True
    assert user_repo.create_user(test_user2) is False


def test_create_duplicate_user(user_repo: UserRepository) -> None:
    test_user1 = User("abc", "efg")
    test_user2 = User("abc", "efg")

    assert user_repo.create_user(test_user1) is True
    assert user_repo.create_user(test_user2) is False


def test_same_username(user_repo: UserRepository) -> None:
    test_user1 = User("abc", "efg")

    assert user_repo.create_user(test_user1) is True
    assert user_repo.username_taken("abc") is True
