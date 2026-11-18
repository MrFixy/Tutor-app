"""Load and query the curated AI Engineering lesson library."""
import json
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from app import models

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_ROOT = REPO_ROOT / "content" / "lessons" / "phases"
CURRICULUM_FILE = REPO_ROOT / "frontend" / "content" / "curriculum.json"


def _parse_lesson_file(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    _, frontmatter_text, body = parts
    return yaml.safe_load(frontmatter_text) or {}, body.strip()


def list_phases() -> list[dict]:
    if not CURRICULUM_FILE.is_file():
        return []
    phases = json.loads(CURRICULUM_FILE.read_text(encoding="utf-8"))
    return [
        {
            "slug": phase["slug"],
            "number": int(phase["number"]),
            "title": phase["title"],
            "lesson_count": len(phase.get("lessons", [])),
        }
        for phase in phases
    ]


def _iter_lesson_files():
    if not CONTENT_ROOT.is_dir():
        return
    for phase_dir in sorted(path for path in CONTENT_ROOT.iterdir() if path.is_dir()):
        for lesson_path in sorted(phase_dir.glob("*.md")):
            yield phase_dir.name, lesson_path


def load_lessons_from_disk(db: Session) -> int:
    """Upsert AI Engineering phase lessons; the Markdown files remain source of truth."""
    count = 0
    for phase_slug, path in _iter_lesson_files():
        frontmatter, body = _parse_lesson_file(path)
        lesson_slug = path.stem
        subtopic = f"{phase_slug}__{lesson_slug}"
        title = frontmatter.get("title") or lesson_slug.replace("-", " ").title()
        order = int(frontmatter.get("order", 0))
        row = (
            db.query(models.LessonContent)
            .filter_by(domain="phases", subtopic=subtopic, language=phase_slug)
            .one_or_none()
        )
        if row is None:
            row = models.LessonContent(domain="phases", subtopic=subtopic, language=phase_slug)
            db.add(row)
        row.title = title
        row.body = body
        row.order = order
        try:
            source_note = path.relative_to(REPO_ROOT)
        except ValueError:
            # Tests and custom imports may supply a content root outside the repo.
            source_note = Path(phase_slug) / path.name
        row.source_note = str(source_note)
        count += 1
    db.commit()
    return count


def get_phase_lesson(db: Session, phase_slug: str, lesson_slug: str):
    subtopic = f"{phase_slug}__{lesson_slug}"
    return (
        db.query(models.LessonContent)
        .filter_by(domain="phases", subtopic=subtopic, language=phase_slug)
        .one_or_none()
    )
