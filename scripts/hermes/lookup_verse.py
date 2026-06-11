#!/usr/bin/env python3
"""Look up verse text from the local Shaul scripture corpus."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTURES = ROOT / "docs" / "scriptures"

# TTH/Delitzsch book slug -> OE folder name (when different)
OE_BOOK_MAP = {
    "tehilim": "psalms",
    "bereshit": "genesis",
    "shemot": "exodus",
    "vaikra": "leviticus",
    "bamidbar": "numbers",
    "devarim": "deuteronomy",
    "ieshaiahu": "isaiah",
    "irmeiahu": "jeremiah",
    "iejezkel": "ezekiel",
    "hoshea": "hosea",
    "ioel": "joel",
    "ionah": "jonah",
    "micah": "micah",
    "iejoshua": "joshua",
    "iehoshua": "joshua",
    "shoftim": "judges",
    "shemuel_alef": "1samuel",
    "shemuel_bet": "2samuel",
    "melajim_alef": "1kings",
    "melajim_bet": "2kings",
    "mishlei": "proverbs",
    "zejariah": "zechariah",
}

# TTH slug -> Delitzsch filename stem
# Alias tags used in notes -> TTH/Delitzsch book slug
BOOK_ALIASES = {
    "romanim": "romanos",
    "qorintiyim_alef": "corinthians1",
    "qorintiyim_bet": "corinthians2",
    "matityahu": "matthew",
    "maasei": "acts",
    "maasei_hashlijim": "acts",
    "qolasim": "colossians",
    "kefa_alef": "peter1",
    "kefa_bet": "peter2",
}

DELITZSCH_MAP = {
    "iojanan": "john",
    "matityahu": "matthew",
    "markos": "mark",
    "lukas": "luke",
    "maasei_hashlijim": "acts",
    "romanos": "romans",
    "qorintiyim_alef": "corinthians1",
    "qorintiyim_bet": "corinthians2",
    "galatim": "galatians",
    "efesim": "ephesians",
    "pilipim": "philippians",
    "philipim": "philippians",
    "qolosim": "colossians",
    "tito": "titus",
    "ivrim": "hebrews",
    "iaakov": "james",
    "iaakov_alef": "james",
    "kefa_alef": "peter1",
    "kefa_bet": "peter2",
    "iehudah": "jude",
    "sodot": "revelation",
    "qolasim": "colossians",
}


def parse_ref(tag: str) -> tuple[str, int, int]:
    tag = tag.strip().lstrip("#")
    match = re.match(r"([a-z0-9_]+)_(\d+)_(\d+)$", tag)
    if not match:
        raise ValueError(f"Invalid verse tag: {tag}")
    return match.group(1), int(match.group(2)), int(match.group(3))


def strip_nikud(text: str) -> str:
    return re.sub(r"[\u0591-\u05C7]", "", text)


def lookup_tth(book: str, chapter: int, verse: int) -> str | None:
    path = SCRIPTURES / "tth" / "json" / f"{book}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    for ch in data.get("chapters", []):
        if ch.get("chapter") == chapter:
            for v in ch.get("verses", []):
                if v.get("verse") == verse:
                    return re.sub(r"</?em>", "", v.get("tth", ""))
    return None


def lookup_delitzsch(book: str, chapter: int, verse: int) -> str | None:
    stem = DELITZSCH_MAP.get(book, book)
    path = SCRIPTURES / "delitzsch" / "json" / f"{stem}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    for ch in data.get("chapters", []):
        if ch.get("number") == chapter:
            for v in ch.get("verses", []):
                if v.get("number") == verse:
                    return strip_nikud(v.get("text_nikud", ""))
    return None


def lookup_oe(book: str, chapter: int, verse: int) -> str | None:
    oe_book = OE_BOOK_MAP.get(book, book)
    path = SCRIPTURES / "oe" / "json" / oe_book / f"{chapter}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    verses = data if isinstance(data, list) else data.get("verses", [])
    for v in verses:
        if v.get("verse") == verse:
            if v.get("hebrew_no_nikud"):
                return v["hebrew_no_nikud"]
            text = v.get("text") or v.get("hebrew", "")
            return strip_nikud(text)
    return None


def lookup(tag: str) -> dict[str, str | None]:
    book, chapter, verse = parse_ref(tag)
    book = BOOK_ALIASES.get(book, book)
    return {
        "tag": f"#{book}_{chapter}_{verse}",
        "tth": lookup_tth(book, chapter, verse),
        "delitzsch": lookup_delitzsch(book, chapter, verse),
        "oe": lookup_oe(book, chapter, verse),
    }


def main() -> None:
    tags = sys.argv[1:]
    if not tags:
        print("Usage: lookup_verse.py #book_ch_v [#book_ch_v ...]", file=sys.stderr)
        sys.exit(1)
    for tag in tags:
        result = lookup(tag)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()