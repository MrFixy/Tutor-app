"""Import AI Engineering from Scratch lesson markdown into Tutor.

TODO: Import lesson code and outputs in a separate feature once the UI supports them.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

REPOSITORY_URL = "https://github.com/rohitg00/ai-engineering-from-scratch.git"
PHASE_PATTERN = re.compile(r"^(\d+)-(.+)$")
H1_PATTERN = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
MOTTO_PATTERN = re.compile(r"^>\s*(.+?)\s*$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, help="Existing source checkout")
    parser.add_argument("--output-dir", type=Path, default=Path("content/lessons/phases"))
    parser.add_argument("--frontend-dir", type=Path, default=Path("frontend/content"))
    return parser.parse_args()


def checkout_source(source_dir: Path | None) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    if source_dir is not None:
        return source_dir, None
    temp_dir = tempfile.TemporaryDirectory(prefix="ai-eng-curriculum-")
    checkout = Path(temp_dir.name) / "source"
    subprocess.run(
        ["git", "clone", "--depth", "1", REPOSITORY_URL, str(checkout)],
        check=True,
    )
    return checkout, temp_dir


def lesson_content(source_path: Path) -> tuple[str, str]:
    text = source_path.read_text(encoding="utf-8")
    title_match = H1_PATTERN.search(text)
    title = title_match.group(1).strip() if title_match else source_path.parent.name
    motto_match = MOTTO_PATTERN.search(text)
    motto = motto_match.group(1).strip() if motto_match else ""
    body = text.strip()
    if title_match:
        body = body[: title_match.start()] + body[title_match.end() :]
    if motto_match:
        adjusted_motto_start = motto_match.start() - (title_match.end() if title_match else 0)
        adjusted_motto_end = motto_match.end() - (title_match.end() if title_match else 0)
        body = body[:adjusted_motto_start] + body[adjusted_motto_end:]
    body = body.strip()
    if motto:
        body = f"*{motto}*\n\n{body}"
    return title, body


def write_frontend_bundle(output_dir: Path, frontend_dir: Path) -> None:
    phases_dir = frontend_dir / "phases"
    if phases_dir.exists():
        shutil.rmtree(phases_dir)
    frontend_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(output_dir, phases_dir)

    manifest = []
    for phase_dir in sorted(path for path in output_dir.iterdir() if path.is_dir()):
        phase_match = PHASE_PATTERN.match(phase_dir.name)
        if phase_match is None:
            continue
        lessons = []
        for path in sorted(phase_dir.glob("*.md")):
            frontmatter, _ = path.read_text(encoding="utf-8").split("---", 2)[1:]
            metadata = yaml.safe_load(frontmatter) or {}
            lessons.append({"slug": path.stem, "title": metadata.get("title", path.stem), "order": metadata.get("order", 0)})
        manifest.append({
            "slug": phase_dir.name,
            "number": int(phase_match.group(1)),
            "title": phase_match.group(2).replace("-", " ").title(),
            "lessons": lessons,
        })
    (frontend_dir / "curriculum.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")


def import_curriculum(source_dir: Path, output_dir: Path, frontend_dir: Path) -> tuple[int, int, int, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for existing_phase in output_dir.iterdir():
        if existing_phase.is_dir():
            shutil.rmtree(existing_phase)
    imported = skipped = total_bytes = phase_count = 0
    phase_dirs = sorted(path for path in (source_dir / "phases").iterdir() if path.is_dir())

    for phase_dir in phase_dirs:
        phase_match = PHASE_PATTERN.match(phase_dir.name)
        if not phase_match:
            print(f"skip phase {phase_dir}: name does not match NN-slug")
            skipped += 1
            continue
        phase_count += 1
        destination_dir = output_dir / phase_dir.name
        destination_dir.mkdir(parents=True, exist_ok=True)
        for lesson_dir in sorted(path for path in phase_dir.iterdir() if path.is_dir()):
            lesson_match = PHASE_PATTERN.match(lesson_dir.name)
            source_path = lesson_dir / "docs" / "en.md"
            if not lesson_match:
                print(f"skip lesson {lesson_dir}: name does not match NN-slug")
                skipped += 1
                continue
            if not source_path.is_file():
                print(f"skip lesson {lesson_dir}: missing docs/en.md")
                skipped += 1
                continue
            lesson_number = int(lesson_match.group(1))
            title, body = lesson_content(source_path)
            destination = destination_dir / f"{lesson_match.group(2)}.md"
            frontmatter = yaml.safe_dump({"title": title, "order": lesson_number}, sort_keys=False).strip()
            output = f"---\n{frontmatter}\n---\n{body}\n"
            destination.write_text(output, encoding="utf-8")
            imported += 1
            total_bytes += len(output.encode("utf-8"))

    write_frontend_bundle(output_dir, frontend_dir)
    return phase_count, imported, skipped, total_bytes


def main() -> None:
    args = parse_args()
    source_dir, temp_dir = checkout_source(args.source_dir)
    try:
        phase_count, imported, skipped, total_bytes = import_curriculum(source_dir, args.output_dir, args.frontend_dir)
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()
    print(f"phases found: {phase_count}")
    print(f"lessons imported: {imported}")
    print(f"lessons skipped: {skipped}")
    print(f"files written: {imported}")
    print(f"bytes written: {total_bytes}")


if __name__ == "__main__":
    main()
