#!/usr/bin/env python3
"""Look up verse text from the local Shaul scripture corpus."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verse_tag_conventions import canonical_book_slug

ROOT = Path(__file__).resolve().parents[1]
SCRIPTURES = ROOT / "docs" / "scriptures"

# TTH/Delitzsch book slug -> OE folder name (when different)
OE_BOOK_MAP = {
    "genesis": "genesis",
    "exodo": "exodus",
    "levitico": "leviticus",
    "numeros": "numbers",
    "deuteronomio": "deuteronomy",
    "josue": "joshua",
    "jueces": "judges",
    "1_samuel": "isamuel",
    "2_samuel": "iisamuel",
    "1_reyes": "ikings",
    "2_reyes": "iikings",
    "isaias": "isaiah",
    "jeremias": "jeremiah",
    "ezequiel": "ezekiel",
    "oseas": "hosea",
    "joel": "joel",
    "jonas": "jonah",
    "miqueas": "micah",
    "nahum": "nahum",
    "habacuc": "habakkuk",
    "sofonias": "zephaniah",
    "hageo": "haggai",
    "zacarias": "zechariah",
    "malaquias": "malachi",
    "salmos": "psalms",
    "proverbios": "proverbs",
    "job": "job",
    "cantares": "songofsolomon",
    "eclesiastes": "ecclesiastes",
    "rut": "ruth",
    "lamentaciones": "lamentations",
    "ester": "esther",
    "daniel": "daniel",
    "esdras": "ezra",
    "nehemias": "nehemiah",
    "1_cronicas": "ichronicles",
    "2_cronicas": "iichronicles",
    "tehilim": "psalms",
    "bereshit": "genesis",
    "shemot": "exodus",
    "vaikra": "leviticus",
    "bamidbar": "numbers",
    "devarim": "deuteronomy",
    "yeshayahu": "isaiah",
    "yirmeyahu": "jeremiah",
    "yejezkel": "ezekiel",
    "hoshea": "hosea",
    "yoel": "joel",
    "ionah": "jonah",
    "micah": "micah",
    "yehoshua": "joshua",
    "shoftim": "judges",
    "shemuel_alef": "1samuel",
    "shemuel_bet": "2samuel",
    "melajim_alef": "1kings",
    "melajim_bet": "2kings",
    "mishlei": "proverbs",
    "qohelet": "ecclesiastes",
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
    "mateo": "matthew",
    "marcos": "mark",
    "lucas": "luke",
    "juan": "john",
    "1_juan": "john1",
    "2_juan": "john2",
    "3_juan": "john3",
    "hechos": "acts",
    "romanos": "romans",
    "1_corintios": "corinthians1",
    "2_corintios": "corinthians2",
    "galatas": "galatians",
    "efesios": "ephesians",
    "filipenses": "philippians",
    "colosenses": "colossians",
    "1_tesalonicenses": "thessalonians1",
    "2_tesalonicenses": "thessalonians2",
    "1_timoteo": "timothy1",
    "2_timoteo": "timothy2",
    "tito": "titus",
    "filemon": "philemon",
    "hebreos": "hebrews",
    "santiago": "james",
    "1_pedro": "peter1",
    "2_pedro": "peter2",
    "judas": "jude",
    "apocalipsis": "revelation",
    "yojanan": "john",
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
    "yaakov": "james",
    "iaakov_alef": "james",
    "kefa_alef": "peter1",
    "kefa_bet": "peter2",
    "yehudah": "jude",
    "sodot": "revelation",
    "qolasim": "colossians",
    "qohelet": "ecclesiastes",
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
    tth_book = {
        "genesis": "bereshit",
        "exodo": "shemot",
        "levitico": "vaikra",
        "numeros": "bamidbar",
        "deuteronomio": "devarim",
        "josue": "iehoshua",
        "jueces": "shoftim",
        "isaias": "ieshaiahu",
        "jeremias": "irmeiahu",
        "ezequiel": "iejezkel",
        "oseas": "hoshea",
        "joel": "ioel",
        "juan": "iojanan",
        "hechos": "maasei_hashlijim",
        "romanos": "romanos",
        "galatas": "galatim",
        "efesios": "efesim",
        "colosenses": "qolasim",
        "santiago": "yaakov",
        "judas": "yehudah",
        "apocalipsis": "sodot",
    }.get(book, book)
    path = SCRIPTURES / "tth" / "json" / f"{tth_book}.json"
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
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        verses = data if isinstance(data, list) else data.get("verses", [])
        for v in verses:
            if v.get("verse") == verse:
                if v.get("hebrew_no_nikud"):
                    return v["hebrew_no_nikud"]
                text = v.get("text") or v.get("hebrew", "")
                return strip_nikud(text)

    # Some OE books currently exist only in the upstream-shaped raw corpus.
    # Keep authoring unblocked while preserving the normal chapter-file lookup.
    raw_path = SCRIPTURES / "oe" / "json" / "raw" / f"{oe_book}.json"
    if not raw_path.exists():
        return None
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    try:
        tokens = raw[chapter - 1][verse - 1]
    except (IndexError, TypeError):
        return None
    return strip_nikud(" ".join(token[0] for token in tokens if token))


def lookup(tag: str) -> dict[str, str | None]:
    book, chapter, verse = parse_ref(tag)
    book = canonical_book_slug(book) or BOOK_ALIASES.get(book, book)
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
