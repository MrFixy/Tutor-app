"""
Phase 6 / Week 14 -- regression test for the bug described in
app/user_service.py: /chat and /practice/*/generate wrote `questions` rows
referencing client-generated user_id/session_id values with no matching
row in `users`/`sessions`, which violates their FK constraints against a
real Postgres schema. No live services needed: only the two tables under
test are created, on an in-memory sqlite engine (sqlite doesn't enforce
FKs by default, so this asserts get_or_create_* behavior directly rather
than relying on an IntegrityError to prove the bug).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app.db import Base
from app.models import User, SessionModel
from app.user_service import get_or_create_user, get_or_create_session


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    User.__table__.create(bind=engine)
    SessionModel.__table__.create(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_get_or_create_user_inserts_missing_row(db):
    assert db.get(User, 42) is None
    user = get_or_create_user(db, 42)
    db.commit()
    assert user.id == 42
    assert db.get(User, 42) is not None


def test_get_or_create_user_reuses_existing_row(db):
    first = get_or_create_user(db, 7, username="alice")
    db.commit()
    second = get_or_create_user(db, 7, username="ignored-on-reuse")
    db.commit()
    assert first.id == second.id == 7
    assert second.username == "alice"  # not overwritten by the second call


def test_get_or_create_session_none_passes_through(db):
    get_or_create_user(db, 1)
    db.commit()
    assert get_or_create_session(db, None, 1) is None


def test_get_or_create_session_inserts_missing_row(db):
    get_or_create_user(db, 1)
    db.commit()
    session_id = get_or_create_session(db, 999999, 1)
    db.commit()
    assert session_id == 999999
    assert db.get(SessionModel, 999999) is not None
