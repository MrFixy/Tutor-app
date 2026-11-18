"""Create the user and session rows referenced by chat and feedback writes.

The frontend generates stable pilot user IDs and per-session IDs. These
helpers ensure the matching foreign-key rows exist before the API stores
chat history or feedback.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app import models


def get_or_create_user(db: Session, user_id: int, username: Optional[str] = None) -> models.User:
    user = db.get(models.User, user_id)
    if user is not None:
        return user
    # user_id is client-generated (a deterministic hash of the username,
    # not a DB sequence value), so we insert with that explicit id rather
    # than letting the users.id SERIAL default assign one.
    user = models.User(id=user_id, username=username or f"pilot-user-{user_id}")
    db.add(user)
    db.flush()  # id already set explicitly, but flush surfaces any conflict now
    return user


def get_or_create_session(db: Session, session_id: Optional[int], user_id: int) -> Optional[int]:
    """Returns the session id to actually store (None passes through)."""
    if session_id is None:
        return None
    existing = db.get(models.SessionModel, session_id)
    if existing is not None:
        return existing.id
    session = models.SessionModel(id=session_id, user_id=user_id)
    db.add(session)
    db.flush()
    return session.id
