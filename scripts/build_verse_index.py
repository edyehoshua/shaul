#!/usr/bin/env python3
"""Build a deterministic, verse-addressable static index from Shaul notes.

Markdown remains the canonical authoring format. This script reads each note's
frontmatter and emits lightweight JSON documents that a Bible reader or an API
wrapper can query without parsing Markdown at request time.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTENT_DIR = ROOT / "content"
DEFAULT_OUTPUT_DIR = ROOT / "static" / "api" / "v1" / "verse-notes"
VERSE_TAG_RE = re.compile(r"^#([a-z0-9_]+)_(\d+)_(\d+)$")
CHAPTER_TAG_RE = re.compile(r"^#([a-z0-9_]+)_(\d+)$")
VERSE_RANGE_TAG_RE = re.compile(r"^#([a-z0-9_]+)_(\d+)_(\d+)-(\d+)$")


class FrontmatterError(ValueError):
    """Raised when a note cannot be represented safely in the static index."""


def scalar(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def inline_list(value: str) -> list[str] | None:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return None
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [scalar(item) for item in inner.split(",") if item.strip()]


def parse_frontmatter(path: Path) -> dict[str, str | list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise FrontmatterError(f"{path}: missing YAML frontmatter")

    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise FrontmatterError(f"{path}: frontmatter is not closed") from error

    result: dict[str, str | list[str]] = {}
    current_list: str | None = None
    for line_number, raw_line in enumerate(lines[1:end], start=2):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("  - "):
            if current_list is None:
                raise FrontmatterError(
                    f"{path}:{line_number}: list item has no parent key"
                )
            value = result.setdefault(current_list, [])
            if not isinstance(value, list):
                raise FrontmatterError(
                    f"{path}:{line_number}: mixed scalar and list value for {current_list}"
                )
            value.append(scalar(raw_line[4:]))
            continue
        if raw_line.startswith((" ", "\t")):
            raise FrontmatterError(
                f"{path}:{line_number}: unsupported frontmatter indentation"
            )
        if ":" not in raw_line:
            raise FrontmatterError(f"{path}:{line_number}: expected key: value")
        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        current_list = key if not value else None
        parsed_list = inline_list(value) if value else []
        result[key] = parsed_list if parsed_list is not None else scalar(value)
    return result


def as_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def note_record(path: Path, content_dir: Path) -> tuple[dict[str, Any], list[str]]:
    frontmatter = parse_frontmatter(path)
    relative_path = path.relative_to(content_dir.parent).as_posix()
    references = as_list(frontmatter.get("references"))
    if not references:
        return {}, []

    normalized_references: list[str] = []
    for reference in references:
        range_match = VERSE_RANGE_TAG_RE.fullmatch(reference)
        if range_match:
            book, chapter, start, end = range_match.groups()
            if int(end) < int(start):
                raise FrontmatterError(
                    f"{path}: invalid descending verse range {reference!r}"
                )
            normalized_references.extend(
                f"#{book}_{chapter}_{verse}"
                for verse in range(int(start), int(end) + 1)
            )
        elif VERSE_TAG_RE.fullmatch(reference) or CHAPTER_TAG_RE.fullmatch(reference):
            normalized_references.append(reference)
        # Legacy notes sometimes carry non-scriptural bibliographic shorthand
        # (for example #berajot_2a) in references. Keep the note intact but do
        # not expose that shorthand as a Bible endpoint.
        else:
            continue

    note = {
        "id": relative_path.removesuffix(".md"),
        "path": relative_path,
        "url": "/" + relative_path.removesuffix(".md") + "/",
        "title": str(frontmatter.get("title", path.stem)),
        "description": str(frontmatter.get("description", "")),
        "tags": as_list(frontmatter.get("tags")),
        "sources": as_list(frontmatter.get("sources")),
        "source_ids": as_list(frontmatter.get("source_ids")),
    }
    return note, sorted(set(normalized_references))


def verse_document(tag: str, notes: list[dict[str, Any]]) -> dict[str, Any]:
    match = VERSE_TAG_RE.fullmatch(tag)
    assert match is not None
    book, chapter, verse = match.groups()
    return {
        "schema_version": 1,
        "verse": {
            "tag": tag,
            "book": book,
            "chapter": int(chapter),
            "verse": int(verse),
        },
        "notes": sorted(notes, key=lambda item: (item["path"], item["title"])),
    }


def chapter_document(tag: str, notes: list[dict[str, Any]]) -> dict[str, Any]:
    match = CHAPTER_TAG_RE.fullmatch(tag)
    assert match is not None
    book, chapter = match.groups()
    return {
        "schema_version": 1,
        "chapter": {"tag": tag, "book": book, "chapter": int(chapter)},
        "notes": sorted(notes, key=lambda item: (item["path"], item["title"])),
    }


def build_index(
    content_dir: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_verse: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in sorted(content_dir.rglob("*.md")):
        note, references = note_record(path, content_dir)
        for reference in references:
            if VERSE_TAG_RE.fullmatch(reference):
                by_verse[reference].append(note)
            else:
                by_chapter[reference].append(note)
    return ({
        tag: verse_document(tag, notes)
        for tag, notes in sorted(by_verse.items())
    }, {
        tag: chapter_document(tag, notes)
        for tag, notes in sorted(by_chapter.items())
    })


def write_index(
    verse_index: dict[str, dict[str, Any]],
    chapter_index: dict[str, dict[str, Any]],
    output_dir: Path,
) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    aggregate = {
        "schema_version": 1,
        "entry_count": len(verse_index),
        "verses": list(verse_index.values()),
        "chapter_entry_count": len(chapter_index),
        "chapters": list(chapter_index.values()),
    }
    (output_dir / "index.json").write_text(
        json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for tag, document in verse_index.items():
        filename = tag.removeprefix("#") + ".json"
        (output_dir / filename).write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    chapters_dir = output_dir / "chapters"
    chapters_dir.mkdir()
    for tag, document in chapter_index.items():
        filename = tag.removeprefix("#") + ".json"
        (chapters_dir / filename).write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-dir", type=Path, default=DEFAULT_CONTENT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    content_dir = args.content_dir.resolve()
    if not content_dir.is_dir():
        raise SystemExit(f"Content directory not found: {content_dir}")
    verse_index, chapter_index = build_index(content_dir)
    write_index(verse_index, chapter_index, args.output_dir.resolve())
    print(
        "Built verse index: "
        f"{len(verse_index)} verses, {len(chapter_index)} chapters -> {args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
