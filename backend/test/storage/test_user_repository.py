"""``SqlUserRepository`` against PostgreSQL ``PH``."""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.storage.user.repository import SqlUserRepository


__all__ = [
    "test_empty_user_count_is_zero",
    "test_add_then_get_by_username",
    "test_duplicate_username_raises_integrity_error",
    "test_count_after_insert_is_one",
]

def test_empty_user_count_is_zero(db_session: Session):
    """Handles test empty user count is zero.


    :param db_session: the db session.
    """
    assert SqlUserRepository(db_session).count() == 0


def test_add_then_get_by_username(db_session: Session):
    """Handles test add then get by username.

    :param db_session: the db session.
    """
    repo = SqlUserRepository(db_session)
    repo.add("alice", "hash1")
    db_session.commit()
    user = repo.get_by_username("alice")
    assert user is not None
    assert user.username == "alice"
    assert user.password_hash == "hash1"


def test_duplicate_username_raises_integrity_error(db_session: Session):
    """Handles test duplicate username raises integrity error.

    :param db_session: the db session.
    """
    repo = SqlUserRepository(db_session)
    repo.add("bob", "h1")
    db_session.commit()
    repo.add("bob", "h2")
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_count_after_insert_is_one(db_session: Session):
    """Handles test count after insert is one.

    :param db_session: the db session.
    """
    repo = SqlUserRepository(db_session)
    repo.add("carol", "h")
    db_session.commit()
    assert repo.count() == 1
