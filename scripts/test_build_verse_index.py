#!/usr/bin/env python3
"""Focused regression tests for scripts/build_verse_index.py."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("build_verse_index.py")
spec = importlib.util.spec_from_file_location("build_verse_index", MODULE_PATH)
assert spec and spec.loader
indexer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indexer)


class VerseIndexTests(unittest.TestCase):
    def write_note(self, directory: Path, body: str) -> None:
        note = directory / "besorah" / "sample.md"
        note.parent.mkdir(parents=True)
        note.write_text(body, encoding="utf-8")

    def test_builds_one_document_per_normalized_verse(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            content = root / "content"
            output = root / "output"
            self.write_note(
                content,
                """---
title: "Sample note"
description: "A stable description"
tags: [yojanan, palabra]
references:
  - "#juan_1_1"
  - "#juan_1_1"
  - "#juan_1_14-15"
sources:
  - "https://www.youtube.com/watch?v=abc123"
---

# Tesis
""",
            )

            verse_index, chapter_index = indexer.build_index(content)
            indexer.write_index(verse_index, chapter_index, output)

            aggregate = json.loads((output / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(aggregate["entry_count"], 3)
            detail = json.loads(
                (output / "juan_1_1.json").read_text(encoding="utf-8")
            )
            self.assertEqual(detail["verse"]["tag"], "#juan_1_1")
            self.assertEqual(detail["notes"][0]["id"], "content/besorah/sample")
            self.assertEqual(detail["notes"][0]["sources"], ["https://www.youtube.com/watch?v=abc123"])

    def test_rejects_malformed_reference_before_emitting_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            content = Path(temp) / "content"
            self.write_note(
                content,
                """---
title: "Broken note"
references:
  - "#juan_1_5-4"
sources: []
---
""",
            )

            with self.assertRaisesRegex(indexer.FrontmatterError, "invalid descending verse range"):
                indexer.build_index(content)

    def test_ignores_hidden_application_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            content = Path(temp) / "content"
            self.write_note(
                content,
                """---
title: "Visible note"
references: ["#juan_1_1"]
sources: []
---
""",
            )
            hidden = content / ".obsidian" / "plugins" / "README.md"
            hidden.parent.mkdir(parents=True)
            hidden.write_text("# Plugin metadata\n", encoding="utf-8")

            verse_index, _ = indexer.build_index(content)

            self.assertEqual(list(verse_index), ["#juan_1_1"])

    def test_accepts_prettier_wrapped_flow_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            content = Path(temp) / "content"
            self.write_note(
                content,
                """---
title: "Flow list"
references: ["#juan_1_1"]
sources:
  [
    "https://www.youtube.com/watch?v=abc123",
    "private/transcripts/ericdejes/abc123.md",
  ]
---
""",
            )

            verse_index, _ = indexer.build_index(content)
            self.assertEqual(
                verse_index["#juan_1_1"]["notes"][0]["sources"],
                [
                    "https://www.youtube.com/watch?v=abc123",
                    "private/transcripts/ericdejes/abc123.md",
                ],
            )


if __name__ == "__main__":
    unittest.main()
