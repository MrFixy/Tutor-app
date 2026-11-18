from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import content_loader, models


@pytest.fixture
def db_and_content_root(tmp_path: Path, monkeypatch):
    for phase_slug in ("00-foundations", "01-agents"):
        phase_dir = tmp_path / phase_slug
        phase_dir.mkdir(parents=True)
        for lesson_number, lesson_slug in ((1, "first-lesson"), (2, "second-lesson")):
            (phase_dir / f"{lesson_slug}.md").write_text(
                f"---\ntitle: {phase_slug} lesson {lesson_number}\norder: {lesson_number}\n---\n\nBody {lesson_number}",
                encoding="utf-8",
            )

    monkeypatch.setattr(content_loader, "CONTENT_ROOT", tmp_path)
    engine = create_engine("sqlite:///:memory:")
    models.LessonContent.__table__.create(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session, tmp_path
    session.close()


def test_loads_only_ai_engineering_phase_lessons(db_and_content_root):
    db, _ = db_and_content_root
    assert content_loader.load_lessons_from_disk(db) == 4
    rows = db.query(models.LessonContent).all()
    assert len(rows) == 4
    assert {row.domain for row in rows} == {"phases"}
    assert {(row.subtopic, row.language) for row in rows} == {
        ("00-foundations__first-lesson", "00-foundations"),
        ("00-foundations__second-lesson", "00-foundations"),
        ("01-agents__first-lesson", "01-agents"),
        ("01-agents__second-lesson", "01-agents"),
    }


def test_gets_lesson_by_phase_and_slug(db_and_content_root):
    db, _ = db_and_content_root
    content_loader.load_lessons_from_disk(db)

    lesson = content_loader.get_phase_lesson(db, "01-agents", "second-lesson")
    assert lesson is not None
    assert lesson.title == "01-agents lesson 2"
    assert lesson.body == "Body 2"
    assert lesson.order == 2
    assert content_loader.get_phase_lesson(db, "99-not-a-real-phase", "missing-lesson") is None
