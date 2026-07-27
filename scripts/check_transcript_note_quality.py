#!/usr/bin/env python3
"""Reject skeletal transcript-derived notes and private transcript paths."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
ID_RE = re.compile(r"youtube:[A-Za-z0-9_-]+")
HEADING_RE = re.compile(r"^##\s+(.+)$", re.M)
WORD_RE = re.compile(r"[\wáéíóúüñÁÉÍÓÚÜÑ]{3,}")
STANDARD_HEADINGS = {
    "tesis",
    "alcance de la nota",
    "hoja de comparación",
    "texto base",
    "pendiente de verificar",
    "conclusión",
    "ver también",
    "créditos",
    "lectura inicial",
    "lectura",
}


def prose_words(body: str) -> int:
    body = re.sub(r"^---.*?---\s*", "", body, flags=re.S)
    body = body.split("## Créditos", 1)[0]
    body = re.sub(r"^\|.*\|\s*$", "", body, flags=re.M)
    body = re.sub(r"^#{1,6}\s+.*$", "", body, flags=re.M)
    body = re.sub(r"`[^`]+`", "", body)
    return len(WORD_RE.findall(body))


def main() -> int:
    failures: list[str] = []
    checked = 0
    selected = [Path(arg) for arg in sys.argv[1:]]
    paths = selected if selected else sorted(CONTENT.rglob("*.md"))
    for path in paths:
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file() or path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not ID_RE.search(text):
            continue
        checked += 1
        rel = path.relative_to(ROOT)
        if "private/transcripts/" in text:
            failures.append(f"{rel}: exposes a private transcript path")
        if re.search(r"[\u0590-\u05FF]/|/[\u0590-\u05FF]", text):
            failures.append(f"{rel}: contains unnormalized Hebrew slash segmentation")
        words = prose_words(text)
        headings = [h.strip().lower() for h in HEADING_RE.findall(text)]
        thematic = [h for h in headings if h not in STANDARD_HEADINGS]
        if words < 300:
            failures.append(f"{rel}: only {words} substantive prose words (minimum 300)")
        if len(thematic) < 2:
            failures.append(f"{rel}: needs at least two transcript-specific thematic sections")
        if "## Lectura inicial" in text and not thematic:
            failures.append(f"{rel}: Lectura inicial is not a sufficient development section")
    print(f"checked_transcript_notes={checked}")
    if failures:
        print(f"quality_failures={len(failures)}")
        print("\n".join(failures))
        return 1
    print("quality_failures=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
