from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import content_loader, models, study_plan


@pytest.fixture
def db_and_content_root(tmp_path: Path, monkeypatch):
    phases = tmp_path / "phases"
    for phase_slug in ("00-foundations", "01-agents"):
        phase_dir = phases / phase_slug
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


def test_loads_phase_lessons_with_composite_keys(db_and_content_root):
    db, _ = db_and_content_root

    assert content_loader.load_lessons_from_disk(db) == 4
    rows = db.query(models.LessonContent).filter_by(domain="phases").all()

    assert {(row.subtopic, row.language) for row in rows} == {
        ("00-foundations__first-lesson", "00-foundations"),
        ("00-foundations__second-lesson", "00-foundations"),
        ("01-agents__first-lesson", "01-agents"),
        ("01-agents__second-lesson", "01-agents"),
    }


def test_lists_and_gets_phase_lessons(db_and_content_root):
    db, _ = db_and_content_root
    content_loader.load_lessons_from_disk(db)

    all_items = study_plan.list_lesson_items(db, 1, domain="phases")
    phase_items = study_plan.list_lesson_items(db, 1, domain="phases", language="01-agents")
    lesson = study_plan.get_lesson(db, "phases", "01-agents__second-lesson", "01-agents")

    assert len(all_items) == 4
    assert all(item.status == "not_started" for item in all_items)
    assert [item.subtopic for item in phase_items] == [
        "01-agents__first-lesson",
        "01-agents__second-lesson",
    ]
    assert lesson is not None
    assert lesson.body == "Body 2"