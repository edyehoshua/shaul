#!/usr/bin/env python3
"""Validate stable metadata and public-facing hygiene for YouTube notes."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from repair_youtube_notes import (
    CONTENT,
    ROOT,
    SOURCE_ID_RE,
    YOUTUBE_URL_RE,
    existing_source_ids,
    is_youtube_note,
    split_frontmatter,
)
from verse_tag_conventions import TAG_TOKEN_RE, canonicalize_tag

VERSE_HEADING_RE = re.compile(r"^##\s+.*?(?<!\w)\d+:\d+(?:[-–]\d+)?\)?\s*$")
UNFORMATTED_SOURCE_ID_RE = re.compile(r"(?<!`)source_id\s*:")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Optional note paths; defaults to all content Markdown files")
    args = parser.parse_args()
    paths = [ROOT / value if not Path(value).is_absolute() else Path(value) for value in args.paths]
    if not paths:
        paths = sorted(CONTENT.rglob("*.md"))

    failures: list[str] = []
    checked = 0
    for path in paths:
        if not path.is_file() or path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(text)
        if parts is None:
            continue
        _, frontmatter, _ = parts
        direct_ids = {match.group(1) for match in YOUTUBE_URL_RE.finditer(frontmatter)}
        if not is_youtube_note(frontmatter) and not direct_ids:
            continue
        checked += 1
        rel = path.relative_to(ROOT)
        metadata_ids = set(SOURCE_ID_RE.findall(frontmatter))
        if direct_ids - metadata_ids:
            failures.append(f"{rel}: missing source_ids for {', '.join(sorted(direct_ids - metadata_ids))}")
        source_id_values = SOURCE_ID_RE.findall(frontmatter)
        if len(source_id_values) != len(set(source_id_values)):
            failures.append(f"{rel}: duplicate source_ids in frontmatter")
        if direct_ids and "## Créditos" not in text:
            failures.append(f"{rel}: missing visible Créditos section")
        for marker in ("npm run", "private/sources/", "private/transcripts/"):
            if marker in text:
                failures.append(f"{rel}: exposes {marker}")
        if UNFORMATTED_SOURCE_ID_RE.search(text):
            failures.append(f"{rel}: source_id credit is not normalized")
        for line in text.splitlines():
            if VERSE_HEADING_RE.match(line) and "#" not in line[3:]:
                failures.append(f"{rel}: verse heading is missing an inline tag: {line}")
        for token in TAG_TOKEN_RE.findall(text):
            canonical = canonicalize_tag(token)
            if canonical and canonical != token:
                failures.append(f"{rel}: non-canonical verse tag {token}; use {canonical}")

    print(f"checked_youtube_notes={checked}")
    print(f"youtube_note_failures={len(failures)}")
    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
