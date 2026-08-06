#!/usr/bin/env python3
"""Check and repair deterministic defects in YouTube-backed public notes.

The repair is intentionally conservative. It only derives stable YouTube IDs
from URLs already present in frontmatter, removes private source paths from
frontmatter, normalizes public credit syntax, removes exposed authoring
commands, and adds verse tags to section headings when the note's existing
frontmatter identifies an unambiguous reference.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
YOUTUBE_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:youtube\.com/(?:watch\?v=|live/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)
SOURCE_ID_RE = re.compile(r"youtube:([A-Za-z0-9_-]{11})")
REF_TAG_RE = re.compile(r"#[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)?")
HEADING_LOCATOR_RE = re.compile(r"(?<!\w)(\d+):(\d+)(?:[-–](\d+))?")
HEADING_CROSS_LOCATOR_RE = re.compile(r"(?<!\w)(\d+):(\d+)[-–](\d+):(\d+)")
TOP_LEVEL_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*:")
BOOK_ALIASES = {
    "amos": {"amos"},
    "bereshit": {"bereshit", "genesis", "génesis"},
    "galatians": {"galatians", "galatim"},
    "iejezkel": {"iejezkel", "yejezkel", "ezequiel"},
    "shemot": {"shemot", "éxodo", "exodo"},
}


@dataclass(frozen=True)
class Reference:
    tag: str
    book: str
    chapter: int
    start: int
    end: int


def split_frontmatter(text: str) -> tuple[str, str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        # Recover notes written by an earlier version of this repairer that
        # accidentally omitted the closing YAML delimiter.
        heading = text.find("\n# ", 4)
        if heading == -1:
            return None
        return text[:4], text[4:heading], "\n" + text[heading + 1 :]
    return text[:4], text[4:end], text[end + 5 :]


def frontmatter_refs(frontmatter: str) -> list[Reference]:
    refs: list[Reference] = []
    lines = frontmatter.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("references:")), None)
    if start is None:
        return refs
    end = source_block_end(lines, "references") or len(lines)
    for tag in REF_TAG_RE.findall("\n".join(lines[start:end])):
        parts = tag[1:].split("_")
        if len(parts) < 3 or not parts[-2].isdigit():
            continue
        verse_match = re.fullmatch(r"(\d+)(?:-(\d+))?", parts[-1])
        if not verse_match:
            continue
        start = int(verse_match.group(1))
        end = int(verse_match.group(2) or start)
        refs.append(
            Reference(
                tag=tag,
                book="_".join(parts[:-2]),
                chapter=int(parts[-2]),
                start=start,
                end=end,
            )
        )
    return refs


def source_urls_with_text(frontmatter: str) -> list[tuple[str, str]]:
    return [(match.group(0), match.group(1)) for match in YOUTUBE_URL_RE.finditer(frontmatter)]


def public_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def existing_source_ids(frontmatter: str) -> set[str]:
    return {match.group(1) for match in SOURCE_ID_RE.finditer(frontmatter)}


def is_youtube_note(frontmatter: str) -> bool:
    return "source_ids:" in frontmatter or bool(source_urls_with_text(frontmatter))


def source_block_end(lines: list[str], key: str) -> int | None:
    start = next((i for i, line in enumerate(lines) if line.startswith(f"{key}:")), None)
    if start is None:
        return None
    for i in range(start + 1, len(lines)):
        if TOP_LEVEL_KEY_RE.match(lines[i]) and not lines[i].startswith(" "):
            return i
    return len(lines)


def repair_source_metadata(frontmatter: str) -> tuple[str, set[str]]:
    urls = source_urls_with_text(frontmatter)
    video_ids = {video_id for _, video_id in urls}
    if not video_ids:
        return frontmatter, set()

    lines = frontmatter.splitlines()
    source_start = next((i for i, line in enumerate(lines) if line.startswith("sources:")), None)
    if source_start is not None:
        source_end = source_block_end(lines, "sources")
        assert source_end is not None
        lines = [
            line
            for i, line in enumerate(lines)
            if not (source_start < i < source_end and "private/sources/" in line)
        ]

    current = existing_source_ids("\n".join(lines))
    missing = sorted(video_ids - current)
    source_ids_start = next((i for i, line in enumerate(lines) if line.startswith("source_ids:")), None)
    if source_ids_start is None:
        source_end = source_block_end(lines, "sources")
        insert_at = source_end if source_end is not None else len(lines)
        lines[insert_at:insert_at] = ["source_ids:", *[f'  - "youtube:{video_id}"' for video_id in missing]]
    elif missing:
        source_ids_end = source_block_end(lines, "source_ids")
        assert source_ids_end is not None
        lines[source_ids_end:source_ids_end] = [f'  - "youtube:{video_id}"' for video_id in missing]

    return "\n".join(lines) + ("\n" if frontmatter.endswith("\n") else ""), video_ids


def remove_private_paths(frontmatter: str) -> str:
    lines = [line for line in frontmatter.splitlines() if "private/sources/" not in line and "private/transcripts/" not in line]
    return "\n".join(lines) + ("\n" if frontmatter.endswith("\n") else "")


def replace_process_leaks(body: str) -> str:
    replacements = {
        "El texto bíblico se cotejó con los corpus locales OE, TTH y Delitzsch después de ejecutar `npm run scriptures:ensure`.":
            "El texto bíblico se cotejó con los corpus locales OE, TTH y Delitzsch, que ya estaban disponibles en el repositorio.",
        "El corpus local fue comprobado con `npm run scriptures:ensure` el 17 de julio de 2026.":
            "El corpus local fue comprobado el 17 de julio de 2026.",
        "Para Tanaj y Besorah se usó el corpus local disponible, confirmado con `npm run scriptures:ensure` el 17 de julio de 2026.":
            "Para Tanaj y Besorah se usó el corpus local disponible, confirmado el 17 de julio de 2026.",
        "El corpus local fue confirmado con `npm run scriptures:ensure` el 17 de julio de 2026.":
            "El corpus local fue confirmado el 17 de julio de 2026.",
        "- `npm run scriptures:ensure` no pudo ejecutarse porque `npm` no está instalado en este entorno; se usó el corpus local ya presente.":
            "- Se usó el corpus local ya presente en el repositorio; no se expone aquí el comando de preparación.",
    }
    for old, new in replacements.items():
        body = body.replace(old, new)
    body = re.sub(r"`npm run [^`]+`", "el comando de preparación del corpus local", body)
    return body


def normalize_credit_ids(body: str) -> str:
    body = re.sub(r"`source_id\s*:", "`source_id`:", body)
    return re.sub(r"(?<!`)source_id\s*:", "`source_id`:", body)


def remove_private_paths_from_body(body: str) -> str:
    return re.sub(
        r"`private/(?:sources|transcripts)/[^`\s]+`|private/(?:sources|transcripts)/[^\s)]+",
        "la transcripción de trabajo",
        body,
    )


def normalize_text(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFD", value.lower()) if unicodedata.category(char) != "Mn"
    )


def heading_book_hint(line: str, locator_start: int, books: set[str]) -> str | None:
    hint = normalize_text(line[3:locator_start].replace("_", " "))
    for book in books:
        aliases = BOOK_ALIASES.get(book, {book.replace("_", " ")})
        if any(normalize_text(alias) in hint for alias in aliases):
            return book
    return None


def choose_reference(
    refs: list[Reference],
    chapter: int,
    start: int,
    end: int,
    preferred_book: str | None = None,
    fallback_book: str | None = None,
) -> str | None:
    candidates = [ref for ref in refs if ref.chapter == chapter and ref.start <= end and ref.end >= start]
    if not candidates:
        candidates = [ref for ref in refs if ref.chapter == chapter]
    if preferred_book:
        preferred = [ref for ref in candidates if ref.book == preferred_book]
        if preferred:
            candidates = preferred
    if not candidates:
        if fallback_book:
            return f"#{fallback_book}_{chapter}_{start}" + (f"-{end}" if end != start else "")
        books = {ref.book for ref in refs}
        if len(books) == 1:
            book = next(iter(books))
            return f"#{book}_{chapter}_{start}" + (f"-{end}" if end != start else "")
        return None
    counts = collections.Counter(ref.book for ref in candidates)
    book, count = counts.most_common(1)[0]
    if len([candidate for candidate in counts.values() if candidate == count]) > 1:
        return None
    return f"#{book}_{chapter}_{start}" + (f"-{end}" if end != start else "")


def add_heading_tags(body: str, refs: list[Reference], primary_book: str | None) -> tuple[str, int, list[str]]:
    changed = 0
    unresolved: list[str] = []
    output: list[str] = []
    for line in body.splitlines(keepends=True):
        if not line.startswith("## ") or "#" in line[3:]:
            output.append(line)
            continue
        cross_locators = list(HEADING_CROSS_LOCATOR_RE.finditer(line))
        locators = [
            locator
            for locator in HEADING_LOCATOR_RE.finditer(line)
            if not any(locator.start() >= cross.start() and locator.end() <= cross.end() for cross in cross_locators)
        ]
        if not locators and not cross_locators:
            output.append(line)
            continue
        tags: list[str] = []
        books = {ref.book for ref in refs}
        for locator in cross_locators:
            preferred_book = heading_book_hint(line, locator.start(), books)
            first = choose_reference(
                refs, int(locator.group(1)), int(locator.group(2)), int(locator.group(2)), preferred_book, primary_book
            )
            second = choose_reference(
                refs, int(locator.group(3)), int(locator.group(4)), int(locator.group(4)), preferred_book, primary_book
            )
            for tag in (first, second):
                if tag and tag not in tags:
                    tags.append(tag)
            if not first or not second:
                unresolved.append(line.rstrip("\n"))
        for locator in locators:
            chapter = int(locator.group(1))
            start = int(locator.group(2))
            end = int(locator.group(3) or start)
            preferred_book = heading_book_hint(line, locator.start(), books)
            tag = choose_reference(refs, chapter, start, end, preferred_book, primary_book)
            if tag and tag not in tags:
                tags.append(tag)
            elif not tag:
                unresolved.append(line.rstrip("\n"))
        if not tags:
            output.append(line)
            continue
        newline = "\n" if line.endswith("\n") else ""
        output.append(line.rstrip("\n") + " " + " ".join(tags) + newline)
        changed += 1
    return "".join(output), changed, unresolved


def append_credits(body: str, urls: list[tuple[str, str]], eric_ids: set[str]) -> str:
    if "## Créditos" in body or not urls:
        return body
    ids = list(dict.fromkeys(video_id for _, video_id in urls))
    url = public_url(ids[0])
    lines = ["", "## Créditos", ""]
    if any(video_id in eric_ids for video_id in ids):
        lines.append("- Expositor: **hermano Eric de Jesús Rodríguez Mendoza**.")
    lines.append(f"- Video público: [Fuente de la clase]({url}) (`source_id`: `youtube:{ids[0]}`).")
    lines.append("- Esta nota organiza y contrasta la exposición; no presenta la transcripción automática como cita literal.")
    return body.rstrip() + "\n" + "\n".join(lines) + "\n"


def repair_text(text: str, eric_ids: set[str]) -> tuple[str, dict[str, int | list[str]]]:
    parts = split_frontmatter(text)
    if parts is None:
        return text, {"changed": 0, "headings": 0, "unresolved": []}
    opening, frontmatter, body = parts
    before = text
    youtube_note = is_youtube_note(frontmatter)
    if youtube_note:
        frontmatter, _ = repair_source_metadata(frontmatter)
    frontmatter = remove_private_paths(frontmatter)
    body = replace_process_leaks(body)
    body = remove_private_paths_from_body(body)
    body = normalize_credit_ids(body)
    heading_count = 0
    unresolved: list[str] = []
    if youtube_note:
        refs = frontmatter_refs(frontmatter)
        primary_book = collections.Counter(ref.book for ref in refs).most_common(1)[0][0] if refs else None
        body, heading_count, unresolved = add_heading_tags(body, refs, primary_book)
        body = append_credits(body, source_urls_with_text(frontmatter), eric_ids)
    if youtube_note and not body.startswith("\n"):
        body = "\n" + body
    after = opening + frontmatter + "\n---\n" + body
    return after, {
        "changed": int(after != before),
        "headings": heading_count,
        "unresolved": unresolved,
    }


def load_eric_ids() -> set[str]:
    path = ROOT / "data/inventories/ericdejes.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return {video.get("id", "") for video in data.get("videos", [])}


def paths_from_args(values: Iterable[str]) -> list[Path]:
    values = list(values)
    if not values:
        return sorted(CONTENT.rglob("*.md"))
    return [ROOT / value if not Path(value).is_absolute() else Path(value) for value in values]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Optional note paths; defaults to all content Markdown files")
    parser.add_argument("--write", action="store_true", help="Apply deterministic repairs")
    args = parser.parse_args()

    eric_ids = load_eric_ids()
    changed_files = 0
    heading_count = 0
    unresolved: list[tuple[Path, str]] = []
    for path in paths_from_args(args.paths):
        if not path.is_file() or path.suffix != ".md":
            continue
        original = path.read_text(encoding="utf-8", errors="replace")
        repaired, report = repair_text(original, eric_ids)
        if report["changed"]:
            changed_files += 1
            if args.write:
                path.write_text(repaired, encoding="utf-8")
        heading_count += int(report["headings"])
        unresolved.extend((path.relative_to(ROOT), item) for item in report["unresolved"])

    mode = "written" if args.write else "would_change"
    print(f"{mode}_files={changed_files}")
    print(f"heading_tags={heading_count}")
    print(f"unresolved_headings={len(unresolved)}")
    for path, heading in unresolved:
        print(f"{path}: {heading}")
    return 1 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
