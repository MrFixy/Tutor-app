"""
Redesign - static lesson content loader.

Lesson content lives as markdown files under content/lessons/ (repo
root, not app/), each with a small YAML frontmatter block:

    ---
    title: "..."
    order: 1
    ---
    <markdown body>

Directory layout encodes domain/subtopic/language:

    content/lessons/stats/<subtopic>.md
    content/lessons/coding/<language>/<subtopic>.md

This module walks that tree and upserts rows into LessonContent, keyed
on (domain, subtopic, language) -- the files are the source of truth,
the DB table is just a queryable index over them. No LLM call anywhere
in this file; lesson content is curated, not generated.

Called once from main.py's startup(), not per-request.
"""
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from app import models

CONTENT_ROOT = Path(__file__).resolve().parent.parent / "content" / "lessons"


def _parse_lesson_file(path: Path) -> tuple[dict, str]:
    """Splits a lesson markdown file into (frontmatter dict, body str)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    _, fm_text, body = parts
    frontmatter = yaml.safe_load(fm_text) or {}
    return frontmatter, body.strip()


def _iter_lesson_files():
    """Yields (domain, subtopic, language, path) for every lesson file."""
    if not CONTENT_ROOT.is_dir():
        return

    stats_dir = CONTENT_ROOT / "stats"
    if stats_dir.is_dir():
        for path in sorted(stats_dir.glob("*.md")):
            yield "stats", path.stem, None, path

    coding_dir = CONTENT_ROOT / "coding"
    if coding_dir.is_dir():
        for lang_dir in sorted(p for p in coding_dir.iterdir() if p.is_dir()):
            for path in sorted(lang_dir.glob("*.md")):
                yield "coding", path.stem, lang_dir.name, path

    phases_dir = CONTENT_ROOT / "phases"
    if phases_dir.is_dir():
        for phase_dir in sorted(p for p in phases_dir.iterdir() if p.is_dir()):
            for path in sorted(phase_dir.glob("*.md")):
                yield "phases", f"{phase_dir.name}__{path.stem}", phase_dir.name, path


def load_lessons_from_disk(db: Session) -> int:
    """Upserts every content/lessons/**.md file into LessonContent, keyed
    on (domain, subtopic, language). Returns the number of files loaded."""
    count = 0
    for domain, subtopic, language, path in _iter_lesson_files():
        frontmatter, body = _parse_lesson_file(path)
        title = frontmatter.get("title") or subtopic.replace("_", " ").title()
        order = int(frontmatter.get("order", 0))

        row = (
            db.query(models.LessonContent)
            .filter_by(domain=domain, subtopic=subtopic, language=language)
            .one_or_none()
        )
        if row is None:
            row = models.LessonContent(domain=domain, subtopic=subtopic, language=language)
            db.add(row)

        row.title = title
        row.body = body
        row.order = order
        row.source_note = str(path.relative_to(CONTENT_ROOT.parent))
        count += 1

    db.commit()
    return count
