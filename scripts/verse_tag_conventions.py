#!/usr/bin/env python3
"""Canonical book slugs for verse tags, scoped by corpus."""
from __future__ import annotations

import re


# Tags stay ASCII so they remain stable in URLs, Obsidian searches, and the
# generated verse index. Tanaj tags use Hebrew transliterations; Besorah tags
# use Spanish book names. Legacy aliases remain accepted for lookup and
# migration, but authored notes are checked against the corpus-specific maps.
TANAJ = "tanaj"
BESORAH = "besorah"
MIXED = "mixed"

TANAJ_BOOK_ALIASES: dict[str, str] = {}
BESORAH_BOOK_ALIASES: dict[str, str] = {}


def register_corpus(mapping: dict[str, str], canonical: str, *aliases: str) -> None:
    for alias in (canonical, *aliases):
        mapping[alias.lower()] = canonical


def register_tanaj(canonical: str, *aliases: str) -> None:
    register_corpus(TANAJ_BOOK_ALIASES, canonical, *aliases)


def register_besorah(canonical: str, *aliases: str) -> None:
    register_corpus(BESORAH_BOOK_ALIASES, canonical, *aliases)


register_tanaj("bereshit", "genesis")
register_tanaj("shemot", "exodo", "exodus")
register_tanaj("vayikra", "levitico", "leviticus", "vaikra", "vayiqra")
register_tanaj("bamidbar", "numeros", "numbers", "bemidbar")
register_tanaj("devarim", "deuteronomio", "deuteronomy")
register_tanaj("yehoshua", "josue", "joshua", "iejoshua", "iehoshua")
register_tanaj("shoftim", "jueces", "judges")
register_tanaj("shemuel_alef", "1_samuel", "1samuel", "isamuel", "samuel1", "shemuel1", "shemuel_1")
register_tanaj("shemuel_bet", "2_samuel", "2samuel", "shemuel2", "shemuel_2", "shmuel_bet")
register_tanaj("melajim_alef", "1_reyes", "1reyes", "1_kings", "melakhim_alef")
register_tanaj("melajim_bet", "2_reyes", "2reyes", "2_kings", "melakhim_bet")
register_tanaj("yeshayahu", "isaias", "isaiah", "ieshaiahu", "yeshaiahu")
register_tanaj("yirmeyahu", "jeremias", "jeremiah", "irmeiahu", "irmeyahu")
register_tanaj("yejezkel", "ezequiel", "ezekiel", "iejezkel", "yehezqel", "yehezekel", "iechezkel", "iejezqel", "yejizqel", "iechezel")
register_tanaj("hoshea", "oseas", "hosea")
register_tanaj("yoel", "joel", "ioel")
register_tanaj("amos")
register_tanaj("ovadiah", "abdias", "obadiah")
register_tanaj("yonah", "jonas", "jonah", "ionah")
register_tanaj("mijah", "miqueas", "micah", "mijaj")
register_tanaj("najum", "nahum")
register_tanaj("habakuk", "habacuc", "habakkuk", "jabakuk", "habakuk")
register_tanaj("tsefaniah", "sofonias", "tzefaniah")
register_tanaj("jaggai", "hageo", "jagai", "hagai")
register_tanaj("zejariah", "zacarias", "zechariah", "zejariah", "zekharyah", "zecharyah", "zacar_yah")
register_tanaj("malaji", "malaquias", "malachi")
register_tanaj("tehilim", "salmos", "salmo", "psalms", "tehillim")
register_tanaj("mishlei", "proverbios", "proverbs", "mishle")
register_tanaj("iyov", "job", "iyob")
register_tanaj("shir_hashirim", "cantares", "songofsolomon", "song_of_solomon")
register_tanaj("qohelet", "eclesiastes", "ecclesiastes")
register_tanaj("rut", "ruth")
register_tanaj("eijah", "lamentaciones", "lamentations", "ejah")
register_tanaj("ester", "esther")
register_tanaj("daniel")
register_tanaj("ezra", "esdras")
register_tanaj("nejemiah", "nehemias", "nehemiah", "nejemia", "nejemiá")
register_tanaj("divrei_hayamim_alef", "1_cronicas", "1cronicas", "1_chronicles")
register_tanaj("divrei_hayamim_bet", "2_cronicas", "2cronicas", "2_chronicles", "divre_hayamim_bet")

register_besorah("mateo", "matthew", "mattai", "mattityahu", "matityahu", "matiyahu")
register_besorah("marcos", "mark", "markos")
register_besorah("lucas", "lukas", "luqas")
register_besorah("juan", "john", "iojanan", "yojanan")
register_besorah("1_juan", "1_yojanan", "iojanan_alef", "yojanan_alef")
register_besorah("2_juan", "2_yojanan", "iojanan_bet", "yojanan_bet")
register_besorah("3_juan", "3_yojanan", "iojanan_gimel", "yojanan_gimel")
register_besorah("hechos", "acts", "maasei", "maaseh", "maasei_hashlijim", "maasei_ha_shlichim")
register_besorah("romanos", "romans", "romanim", "romiyim", "romaiim")
register_besorah("1_corintios", "1_corinthians", "corinthians1", "first_corinthians", "corintios1", "corintios_1", "corintiyim_alef", "korintim_alef", "qorintiyim_alef", "qorintim_alef")
register_besorah("2_corintios", "2_corinthians", "corinthians2", "corintios2", "corintios_bet", "corintiyim_bet", "korintim_bet", "qorintiyim_bet", "qorintim_bet", "corintim_bet")
register_besorah("galatas", "galatians", "galatim", "galatiyim", "galatiim")
register_besorah("efesios", "ephesians", "efesiyim", "efesim")
register_besorah("filipenses", "filipians", "filipiyim", "filipim")
register_besorah("colosenses", "colossians", "qolasim", "qolosim", "kolosim")
register_besorah("1_tesalonicenses", "1_thessalonians", "thessalonians1", "tesaloniqim_alef", "tesalonicenses_1", "tesalonicenses_alef")
register_besorah("2_tesalonicenses", "2_thessalonians", "thessalonians2", "tesaloniqim_bet", "tesalonicenses_2", "tesalonicenses_bet")
register_besorah("1_timoteo", "1_timothy", "timothy1", "timoteo_alef", "timoteos_alef")
register_besorah("2_timoteo", "2_timothy", "timothy2", "timotheos_bet", "timoteo_bet", "timoteos_bet")
register_besorah("tito")
register_besorah("filemon", "philemon")
register_besorah("hebreos", "hebrews", "ivrim", "ivrit")
register_besorah("santiago", "james", "jacobo", "yaakov", "iaakov", "iaacov", "iaakob", "yeakov")
register_besorah("1_pedro", "1_peter", "peter1", "kefa_alef", "keifa_alef", "keifa")
register_besorah("2_pedro", "2_peter", "peter2", "kefa_bet", "keifa_bet")
register_besorah("judas", "jude", "yehudah")
register_besorah("apocalipsis", "revelation", "sodot", "hitgalut", "jizayon")

# Compatibility map for lookup and repair tooling, which historically returns
# Spanish canonical slugs to resolve source-corpus filenames.
BOOK_ALIASES: dict[str, str] = {}


def register_legacy(canonical: str, *aliases: str) -> None:
    for alias in (canonical, *aliases):
        BOOK_ALIASES[alias.lower()] = canonical


for canonical, aliases in {
    "genesis": ("bereshit",),
    "exodo": ("exodus", "shemot"),
    "levitico": ("leviticus", "vaikra", "vayikra", "vayiqra"),
    "numeros": ("numbers", "bamidbar", "bemidbar"),
    "deuteronomio": ("deuteronomy", "devarim"),
    "josue": ("joshua", "iejoshua", "iehoshua", "yehoshua"),
    "jueces": ("judges", "shoftim"),
    "1_samuel": ("1samuel", "isamuel", "samuel1", "shemuel1", "shemuel_alef", "shemuel_1"),
    "2_samuel": ("2samuel", "shemuel2", "shemuel_bet", "shemuel_2", "shmuel_bet"),
    "1_reyes": ("1reyes", "1_kings", "melajim_alef", "melakhim_alef"),
    "2_reyes": ("2reyes", "2_kings", "melajim_bet", "melakhim_bet"),
    "isaias": ("isaiah", "ieshaiahu", "yeshaiahu", "yeshayahu"),
    "jeremias": ("jeremiah", "irmeiahu", "irmeyahu", "yirmeyahu"),
    "ezequiel": ("ezekiel", "iejezkel", "yejezkel", "yehezqel", "yehezekel", "iechezkel", "iejezqel", "yejizqel", "iechezel"),
    "oseas": ("hosea", "hoshea"),
    "joel": ("ioel", "yoel"),
    "amos": (),
    "abdias": ("obadiah", "ovadiah"),
    "jonas": ("jonah", "ionah", "yonah"),
    "miqueas": ("micah", "mijah", "mijaj"),
    "nahum": ("najum",),
    "habacuc": ("habakkuk", "jabakuk", "habakuk"),
    "sofonias": ("tsefaniah", "tzefaniah"),
    "hageo": ("jagai", "jaggai", "hagai"),
    "zacarias": ("zechariah", "zejariah", "zekharyah", "zecharyah", "zacar_yah"),
    "malaquias": ("malachi", "malaji"),
    "salmos": ("salmo", "psalms", "tehilim", "tehillim"),
    "proverbios": ("proverbs", "mishlei", "mishle"),
    "job": ("iyov", "iyob"),
    "cantares": ("songofsolomon", "song_of_solomon", "shir_hashirim"),
    "eclesiastes": ("ecclesiastes", "qohelet"),
    "rut": ("ruth",),
    "lamentaciones": ("lamentations", "eijah", "ejah"),
    "ester": ("esther",),
    "daniel": (),
    "esdras": ("ezra",),
    "nehemias": ("nehemiah", "nejemiah", "nejemia", "nejemiá"),
    "1_cronicas": ("1cronicas", "1_chronicles", "divrei_hayamim_alef"),
    "2_cronicas": ("2cronicas", "2_chronicles", "divrei_hayamim_bet", "divre_hayamim_bet"),
}.items():
    register_legacy(canonical, *aliases)

for canonical, aliases in {
    "mateo": ("matthew", "mattai", "mattityahu", "matityahu", "matiyahu"),
    "marcos": ("mark", "markos"),
    "lucas": ("lukas", "luqas"),
    "juan": ("john", "iojanan", "yojanan"),
    "1_juan": ("1_yojanan", "iojanan_alef", "yojanan_alef"),
    "2_juan": ("2_yojanan", "iojanan_bet", "yojanan_bet"),
    "3_juan": ("3_yojanan", "iojanan_gimel", "yojanan_gimel"),
    "hechos": ("acts", "maasei", "maaseh", "maasei_hashlijim", "maasei_ha_shlichim"),
    "romanos": ("romans", "romanim", "romiyim", "romaiim"),
    "1_corintios": ("1_corinthians", "corinthians1", "first_corinthians", "corintios1", "corintios_1", "corintiyim_alef", "korintim_alef", "qorintiyim_alef", "qorintim_alef"),
    "2_corintios": ("2_corinthians", "corinthians2", "corintios2", "corintios_bet", "corintiyim_bet", "korintim_bet", "qorintiyim_bet", "qorintim_bet", "corintim_bet"),
    "galatas": ("galatians", "galatim", "galatiyim", "galatiim"),
    "efesios": ("ephesians", "efesiyim", "efesim"),
    "filipenses": ("filipians", "filipiyim", "filipim"),
    "colosenses": ("colossians", "qolasim", "qolosim", "kolosim"),
    "1_tesalonicenses": ("1_thessalonians", "thessalonians1", "tesaloniqim_alef", "tesalonicenses_1", "tesalonicenses_alef"),
    "2_tesalonicenses": ("2_thessalonians", "thessalonians2", "tesaloniqim_bet", "tesalonicenses_2", "tesalonicenses_bet"),
    "1_timoteo": ("1_timothy", "timothy1", "timoteo_alef", "timoteos_alef"),
    "2_timoteo": ("2_timothy", "timothy2", "timotheos_bet", "timoteo_bet", "timoteos_bet"),
    "tito": (),
    "filemon": ("philemon",),
    "hebreos": ("hebrews", "ivrim", "ivrit"),
    "santiago": ("james", "jacobo", "yaakov", "iaakov", "iaacov", "iaakob", "yeakov"),
    "1_pedro": ("1_peter", "peter1", "kefa_alef", "keifa_alef", "keifa"),
    "2_pedro": ("2_peter", "peter2", "kefa_bet", "keifa_bet"),
    "judas": ("jude", "yehudah"),
    "apocalipsis": ("revelation", "sodot", "hitgalut", "jizayon"),
}.items():
    register_legacy(canonical, *aliases)


VERSE_TAG_RE = re.compile(r"#(?P<book>[A-Za-z0-9_]+)_(?P<chapter>\d+)_(?P<verse>\d+(?:-\d+)?)\b")
CHAPTER_TAG_RE = re.compile(r"#(?P<book>[A-Za-z0-9_]+)_(?P<chapter>\d+)\b")
TAG_TOKEN_RE = re.compile(r"#[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)?")


def canonical_book_slug(book: str) -> str | None:
    """Return the legacy Spanish canonical slug used by lookup tooling."""
    return BOOK_ALIASES.get(book.lower())


def canonical_book_slug_for_corpus(book: str, corpus: str) -> str | None:
    """Return the authored canonical slug for a Tanaj or Besorah note."""
    if corpus == TANAJ:
        return TANAJ_BOOK_ALIASES.get(book.lower())
    if corpus == BESORAH:
        return BESORAH_BOOK_ALIASES.get(book.lower())
    raise ValueError(f"Unknown corpus: {corpus}")


def canonical_book_slug_for_corpus_or_citation(book: str, corpus: str | None) -> str | None:
    """Resolve a book in the note corpus, then the other corpus for citations."""
    if corpus is None:
        return canonical_book_slug(book)
    if corpus == MIXED:
        return BESORAH_BOOK_ALIASES.get(book.lower()) or TANAJ_BOOK_ALIASES.get(book.lower())
    canonical = canonical_book_slug_for_corpus(book, corpus)
    if canonical is not None:
        return canonical
    other = BESORAH if corpus == TANAJ else TANAJ
    return canonical_book_slug_for_corpus(book, other)


def corpus_for_path(path: str) -> str | None:
    """Infer the authored corpus from a repository-relative path."""
    parts = path.replace("\\", "/").split("/")
    if "tanaj" in parts:
        return TANAJ
    if "besorah" in parts:
        return BESORAH
    return None


def canonicalize_tag(token: str, corpus: str | None = None) -> str | None:
    """Return a canonical tag, or None when the token is not a known verse tag."""
    match = VERSE_TAG_RE.fullmatch(token)
    if match is None:
        match = CHAPTER_TAG_RE.fullmatch(token)
    if match is not None:
        book = canonical_book_slug_for_corpus_or_citation(match.group("book"), corpus)
        if book is None:
            return None
        suffix = token.removeprefix(f"#{match.group('book')}")
        return f"#{book}{suffix}"

    parts = token.removeprefix("#").split("_")
    for split in range(len(parts) - 1, 0, -1):
        suffix = "_".join(parts[split:])
        if not suffix or not suffix[0].isdigit():
            continue
        book = canonical_book_slug_for_corpus_or_citation("_".join(parts[:split]), corpus)
        if book is not None:
            return f"#{book}_{suffix}"
    return None


def is_known_verse_tag(token: str) -> bool:
    return canonicalize_tag(token) is not None
