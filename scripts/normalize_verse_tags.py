#!/usr/bin/env python3
"""Migrate verse tags to Spanish book slugs and normalize Yod transliteration."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

from verse_tag_conventions import TAG_TOKEN_RE, canonicalize_tag

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
DOCS = ROOT / "docs"
SCRIPTS = ROOT / "scripts"

# These replacements apply to authored visible text, including Markdown table
# cells. Fenced source blocks are left untouched so their source wording stays
# auditable, and the local scripture corpus is excluded from the path set.
NAME_REPLACEMENTS = {
    "Ieshaiahu": "Yeshayahu",
    "ieshaiahu": "yeshayahu",
    "Ieshaiáhu": "Yeshayahu",
    "ieshaiáhu": "yeshayahu",
    "Ieshaiáh": "Yeshaiáh",
    "ieshaiáh": "yeshaiáh",
    "Iaakov": "Yaakov",
    "iaakov": "yaakov",
    "Iaacob": "Yaakov",
    "iaacob": "yaakov",
    "Iacob": "Yaakov",
    "iacob": "yaakov",
    "Iakob": "Yaakov",
    "iakob": "yaakov",
    "Iojanán": "Yojanán",
    "iojanán": "yojanán",
    "Iojanan": "Yojanan",
    "iojanan": "yojanan",
    "Iehoshua": "Yehoshua",
    "iehoshua": "yehoshua",
    "Iejoshua": "Yehoshua",
    "iejoshua": "yehoshua",
    "Iehudáh": "Yehudáh",
    "iehudáh": "yehudáh",
    "Iehudah": "Yehudah",
    "iehudah": "yehudah",
    "Iehú": "Yehú",
    "iehu": "yehu",
    "Iehoásh": "Yehoásh",
    "iehoásh": "yehoásh",
    "Iehoash": "Yehoash",
    "iehoash": "yehoash",
    "Iehoiada": "Yehoiada",
    "iehoiada": "yehoiada",
    "Iehoajaz": "Yehoajaz",
    "iehoajaz": "yehoajaz",
    "Iehoiakim": "Yehoiakim",
    "iehoiakim": "yehoiakim",
    "Iehoshafat": "Yehoshafat",
    "iehoshafat": "yehoshafat",
    "Iehoram": "Yehoram",
    "iehoram": "yehoram",
    "Irmeiahu": "Yirmeyahu",
    "irmeiahu": "yirmeyahu",
    "Irmeyahu": "Yirmeyahu",
    "irmeyahu": "yirmeyahu",
    "Ierushaláim": "Yerushaláim",
    "ierushaláim": "yerushaláim",
    "Ierushalaim": "Yerushalaim",
    "ierushalaim": "yerushalaim",
    "Ierijó": "Yerijó",
    "ierijó": "yerijó",
    "Iardén": "Yardén",
    "iardén": "yardén",
    "Iosef": "Yosef",
    "iosef": "yosef",
    "Ishai": "Yishai",
    "ishai": "yishai",
    "Iair": "Yair",
    "iair": "yair",
    "Iarobam": "Yarobam",
    "iarobam": "yarobam",
    "Iotam": "Yotam",
    "iotam": "yotam",
    "IOTAM": "YOTAM",
    "Ioel": "Yoel",
    "ioel": "yoel",
    "Io'el": "Yo'el",
    "io'el": "yo'el",
    "Iovel": "Yovel",
    "iovel": "yovel",
    "Itzjak": "Yitzjak",
    "itzjak": "yitzjak",
    "Isjak": "Yitzjak",
    "isjak": "yitzjak",
    "Iefté": "Yefté",
    "iefté": "yefté",
    "Iejezkel": "Yejezkel",
    "iejezkel": "yejezkel",
}
NAME_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(value) for value in sorted(NAME_REPLACEMENTS, key=len, reverse=True)) + r")\b"
)


def default_paths() -> list[Path]:
    paths = sorted(CONTENT.rglob("*.md"))
    paths.extend(path for path in sorted(DOCS.rglob("*.md")) if "docs/scriptures/" not in path.as_posix())
    excluded_scripts = {
        "check_verse_tag_conventions.py",
        "lookup_verse.py",
        "normalize_verse_tags.py",
        "test_check_verse_tag_conventions.py",
        "test_normalize_verse_tags.py",
        "verse_tag_conventions.py",
    }
    paths.extend(path for path in sorted(SCRIPTS.glob("*.py")) if path.name not in excluded_scripts)
    return paths


def paths_from_args(values: Iterable[str]) -> list[Path]:
    values = list(values)
    if not values:
        return default_paths()
    return [ROOT / value if not Path(value).is_absolute() else Path(value) for value in values]


def normalize_tags(text: str) -> tuple[str, int, list[str]]:
    changed = 0
    unknown: list[str] = []

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        token = match.group(0)
        canonical = canonicalize_tag(token)
        if canonical is None:
            return token
        if canonical != token:
            changed += 1
        return canonical

    normalized = TAG_TOKEN_RE.sub(replace, text)
    return normalized, changed, unknown


def normalize_names(text: str) -> tuple[str, int]:
    changed = 0
    output: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            output.append(line)
            continue
        if in_fence:
            output.append(line)
            continue

        def replace(match: re.Match[str]) -> str:
            nonlocal changed
            changed += 1
            return NAME_REPLACEMENTS[match.group(0)]

        output.append(NAME_RE.sub(replace, line))
    return "".join(output), changed


def normalize_text(path: Path) -> tuple[str, dict[str, int]]:
    original = path.read_text(encoding="utf-8", errors="replace")
    normalized, tag_count, _ = normalize_tags(original)
    normalized, name_count = normalize_names(normalized)
    return normalized, {"tags": tag_count, "names": name_count, "changed": int(normalized != original)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Optional paths; defaults to authored content, docs, and scripts")
    parser.add_argument("--write", action="store_true", help="Apply the migration")
    args = parser.parse_args()

    files = 0
    tags = 0
    names = 0
    for path in paths_from_args(args.paths):
        if not path.is_file():
            continue
        normalized, report = normalize_text(path)
        files += report["changed"]
        tags += report["tags"]
        names += report["names"]
        if args.write and report["changed"]:
            path.write_text(normalized, encoding="utf-8")

    mode = "written" if args.write else "would_change"
    print(f"{mode}_files={files}")
    print(f"canonicalized_tags={tags}")
    print(f"normalized_names={names}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
