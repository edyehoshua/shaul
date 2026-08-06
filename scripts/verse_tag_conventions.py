#!/usr/bin/env python3
"""Canonical Spanish book slugs used by verse tags."""
from __future__ import annotations

import re


# Tags stay ASCII so they remain stable in URLs, Obsidian searches, and the
# generated verse index. The visible note text may still use Hebrew names.
BOOK_ALIASES: dict[str, str] = {}


def register(canonical: str, *aliases: str) -> None:
    for alias in (canonical, *aliases):
        BOOK_ALIASES[alias.lower()] = canonical


register("genesis", "bereshit")
register("exodo", "exodus", "shemot")
register("levitico", "leviticus", "levitico", "vaikra", "vayikra", "vayiqra")
register("numeros", "numbers", "bamidbar", "bemidbar")
register("deuteronomio", "deuteronomy", "devarim")
register("josue", "joshua", "josue", "iejoshua", "iehoshua", "yehoshua")
register("jueces", "judges", "jueces", "shoftim")
register("1_samuel", "1samuel", "1_samuel", "isamuel", "samuel1", "shemuel1", "shemuel_alef", "shemuel_1")
register("2_samuel", "2samuel", "2_samuel", "shemuel2", "shemuel_bet", "shemuel_2", "shmuel_bet")
register("1_reyes", "1reyes", "1_reyes", "1_kings", "melajim_alef", "melakhim_alef")
register("2_reyes", "2reyes", "2_reyes", "2_kings", "melajim_bet", "melakhim_bet")
register("isaias", "isaiah", "isaias", "ieshaiahu", "yeshaiahu", "yeshayahu")
register("jeremias", "jeremiah", "jeremias", "irmeiahu", "irmeyahu", "yirmeyahu")
register("ezequiel", "ezequiel", "ezekiel", "iejezkel", "yejezkel", "yehezqel", "yehezekel", "iechezkel", "iejezqel", "yejizqel", "iechezel")
register("oseas", "hosea", "hoshea", "oseas")
register("joel", "joel", "ioel", "yoel")
register("amos", "amos")
register("abdias", "abdias", "obadiah", "ovadiah")
register("jonas", "jonah", "jonas", "ionah", "yonah")
register("miqueas", "micah", "miqueas", "mijah", "mijaj")
register("nahum", "nahum", "najum")
register("habacuc", "habacuc", "habakkuk", "jabakuk", "habakuk")
register("sofonias", "sofonias", "tsefaniah", "tzefaniah")
register("hageo", "hageo", "jagai", "jaggai", "hagai")
register("zacarias", "zacarias", "zechariah", "zejariah", "zekharyah", "zecharyah", "zacar_yah")
register("malaquias", "malaquias", "malachi", "malaji")
register("salmos", "salmos", "salmo", "psalms", "tehilim", "tehillim")
register("proverbios", "proverbios", "proverbs", "mishlei", "mishle")
register("job", "job", "iyov", "iyob")
register("cantares", "cantares", "songofsolomon", "song_of_solomon", "shir_hashirim")
register("eclesiastes", "eclesiastes", "ecclesiastes", "qohelet")
register("rut", "rut", "ruth")
register("lamentaciones", "lamentaciones", "lamentations", "eijah", "ejah")
register("ester", "ester", "esther")
register("daniel", "daniel")
register("esdras", "esdras", "ezra")
register("nehemias", "nehemias", "nehemiah", "nejemiah", "nejemia", "nejemiá")
register("1_cronicas", "1cronicas", "1_cronicas", "1_chronicles", "divrei_hayamim_alef")
register("2_cronicas", "2cronicas", "2_cronicas", "2_chronicles", "divrei_hayamim_bet", "divre_hayamim_bet")

register("mateo", "mateo", "matthew", "mattai", "mattityahu", "matityahu", "mattityahu", "matiyahu")
register("marcos", "marcos", "mark", "markos")
register("lucas", "lucas", "lukas", "luqas")
register("juan", "john", "juan", "iojanan", "yojanan")
register("1_juan", "1_juan", "1_yojanan", "iojanan_alef", "yojanan_alef")
register("2_juan", "2_juan", "2_yojanan", "iojanan_bet", "yojanan_bet")
register("3_juan", "3_juan", "3_yojanan", "iojanan_gimel", "yojanan_gimel")
register("hechos", "acts", "hechos", "maasei", "maaseh", "maasei_hashlijim", "maasei_ha_shlichim")
register("romanos", "romanos", "romans", "romanim", "romiyim", "romaiim")
register("1_corintios", "1_corintios", "1_corinthians", "corinthians1", "first_corinthians", "corintios1", "corintios_1", "corintiyim_alef", "korintim_alef", "qorintiyim_alef", "qorintim_alef", "corintiyim_alef")
register("2_corintios", "2_corintios", "2_corinthians", "corinthians2", "corintios2", "corintios_bet", "corintiyim_bet", "korintim_bet", "qorintiyim_bet", "qorintim_bet", "corintim_bet")
register("galatas", "galatas", "galatians", "galatim", "galatiyim", "galatiim")
register("efesios", "efesios", "ephesians", "efesiyim", "efesim")
register("filipenses", "filipenses", "filipians", "filipiyim", "filipim")
register("colosenses", "colosenses", "colossians", "qolasim", "qolosim", "kolosim")
register("1_tesalonicenses", "1_tesalonicenses", "1_thessalonians", "thessalonians1", "tesaloniqim_alef", "tesalonicenses_alef")
register("2_tesalonicenses", "2_tesalonicenses", "2_thessalonians", "thessalonians2", "tesaloniqim_bet", "tesalonicenses_bet")
register("1_timoteo", "1_timoteo", "1_timothy", "timothy1", "timoteo_alef", "timoteos_alef")
register("2_timoteo", "2_timoteo", "2_timothy", "timothy2", "timotheos_bet", "timoteo_bet", "timoteos_bet")
register("tito", "tito")
register("filemon", "filemon", "philemon")
register("hebreos", "hebreos", "hebrews", "ivrim", "ivrit")
register("santiago", "santiago", "james", "jacobo", "yaakov", "iaakov", "iaacov", "iaakob", "yeakov")
register("1_pedro", "1_pedro", "1_peter", "peter1", "kefa_alef", "keifa_alef", "keifa")
register("2_pedro", "2_pedro", "2_peter", "peter2", "kefa_bet", "keifa_bet")
register("judas", "judas", "jude", "yehudah")
register("apocalipsis", "apocalipsis", "revelation", "sodot", "hitgalut", "jizayon")


VERSE_TAG_RE = re.compile(r"#(?P<book>[A-Za-z0-9_]+)_(?P<chapter>\d+)_(?P<verse>\d+(?:-\d+)?)\b")
CHAPTER_TAG_RE = re.compile(r"#(?P<book>[A-Za-z0-9_]+)_(?P<chapter>\d+)\b")
TAG_TOKEN_RE = re.compile(r"#[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)?")


def canonical_book_slug(book: str) -> str | None:
    return BOOK_ALIASES.get(book.lower())


def canonicalize_tag(token: str) -> str | None:
    """Return a canonical tag, or None when the token is not a known verse tag."""
    match = VERSE_TAG_RE.fullmatch(token)
    if match is None:
        match = CHAPTER_TAG_RE.fullmatch(token)
    if match is not None:
        book = canonical_book_slug(match.group("book"))
        if book is None:
            return None
        suffix = token.removeprefix(f"#{match.group('book')}")
        return f"#{book}{suffix}"

    parts = token.removeprefix("#").split("_")
    for split in range(len(parts) - 1, 0, -1):
        suffix = "_".join(parts[split:])
        if not suffix or not suffix[0].isdigit():
            continue
        book = canonical_book_slug("_".join(parts[:split]))
        if book is not None:
            return f"#{book}_{suffix}"
    return None


def is_known_verse_tag(token: str) -> bool:
    return canonicalize_tag(token) is not None
