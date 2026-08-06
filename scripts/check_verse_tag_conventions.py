#!/usr/bin/env python3
"""Check canonical Spanish verse tags and Yod transliteration in authored text."""
from __future__ import annotations

from pathlib import Path

from normalize_verse_tags import CONTENT, DOCS, normalize_names
from verse_tag_conventions import TAG_TOKEN_RE, canonicalize_tag

ROOT = Path(__file__).resolve().parents[1]


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
        for token in TAG_TOKEN_RE.findall(text):
            canonical = canonicalize_tag(token)
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
