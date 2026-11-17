"""
Phase 6 / Week 14 — pilot bug fix (found during pre-pilot smoke testing,
before Week 13 recruiting, so it never actually hit a pilot learner).

Weeks 1-12 never inserted a row into `users` or `sessions` anywhere.
Login.js/store.js only *invent* a client-side user_id (hash of the
username) and session_id (Date.now()), and /chat + /practice/*/generate
wrote `questions` rows referencing those ids directly. Both columns are
real foreign keys (`users.id`, `sessions.id`); against the real Postgres
schema (not sqlite, which doesn't enforce FKs by default) the very first
`/chat` call from a fresh username raises an IntegrityError and the
request 500s. Caught with a local Postgres run before Week 13, not by a
pilot learner's first message -- but it's exactly the kind of thing the
Week 13 survey was designed to catch, so it's logged here as a bug fix
rather than quietly folded in.

get_or_create_user / get_or_create_session make the DB self-healing for
these client-generated ids: reuse the row if it already exists, insert it
with the given id if not. Call both before any write that references
user_id/session_id.
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
