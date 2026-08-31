#!/usr/bin/env python3
"""Check corpus-specific verse tags and Yod transliteration in authored text."""
from __future__ import annotations

from pathlib import Path

from normalize_verse_tags import CONTENT, DOCS, normalize_names
from verse_tag_conventions import (
    MIXED,
    TAG_TOKEN_RE,
    canonical_book_slug_for_corpus_or_citation,
    canonicalize_tag,
    corpus_for_path,
)

ROOT = Path(__file__).resolve().parents[1]


def frontmatter_tag_failures(text: str, corpus: str, path: Path) -> list[str]:
    """Check plain book/chapter tags in YAML, which are not hashtag tokens."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    failures: list[str] = []
    in_frontmatter = True
    in_tags = False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        stripped = line.lstrip()
        if stripped.startswith("tags:"):
            in_tags = True
            continue
        if stripped and not stripped.startswith("-"):
            in_tags = False
        if not in_tags or not line.startswith(("  -", "\t-")):
            continue
        raw = stripped[1:].strip().strip("\"'")
        canonical = canonical_book_slug_for_corpus_or_citation(raw, corpus)
        if canonical is None:
            resolved = canonicalize_tag(f"#{raw}", corpus)
            canonical = resolved.removeprefix("#") if resolved else None
        if canonical is not None and canonical != raw:
            failures.append(f"{path.relative_to(ROOT)}: non-canonical frontmatter book tag {raw} (use {canonical})")
    return failures


def main() -> int:
    failures: list[str] = []
    canonical_tags = 0
    checked_files = 0
    paths = [*sorted(CONTENT.rglob("*.md")), *sorted(DOCS.rglob("*.md"))]
    paths = [path for path in paths if "docs/scriptures/" not in path.as_posix()]
    for path in paths:
        if not path.is_file():
            continue
        checked_files += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        corpus = corpus_for_path(path.as_posix()) or MIXED
        failures.extend(frontmatter_tag_failures(text, corpus, path))
        for token in TAG_TOKEN_RE.findall(text):
            canonical = canonicalize_tag(token, corpus)
            if canonical is None:
                continue
            canonical_tags += 1
            if canonical != token:
                failures.append(f"{path.relative_to(ROOT)}: non-canonical verse tag {token} (use {canonical})")
        normalized, _ = normalize_names(text)
        if normalized != text:
            failures.append(f"{path.relative_to(ROOT)}: contains an old Iod transliteration")

    print(f"checked_authored_files={checked_files}")
    print(f"canonical_verse_tags={canonical_tags}")
    print(f"verse_convention_failures={len(failures)}")
    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
