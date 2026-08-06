#!/usr/bin/env python3
import unittest

from repair_youtube_notes import repair_text


class RepairYouTubeNotesTests(unittest.TestCase):
    def test_repair_is_deterministic_and_idempotent(self) -> None:
        source = """---
title: \"Prueba\"
references:
  - \"#ephesians_1_5\"
  - \"#ephesians_1_6\"
sources:
  - \"https://www.youtube.com/watch?v=abcdefghijk\"
  - \"private/sources/youtube_abcdefghijk_transcript.txt\"
translation: \"[Delitzsch]\"
---

# Tesis

## La adopción y el favor (1:5-6)

El corpus local fue comprobado con `npm run scriptures:ensure` el 17 de julio de 2026.

## Créditos

- Video: [Fuente](https://www.youtube.com/watch?v=abcdefghijk) (source_id: `youtube:abcdefghijk`).
"""
        repaired, report = repair_text(source, {"abcdefghijk"})
        self.assertEqual(report["unresolved"], [])
        self.assertIn('source_ids:\n  - "youtube:abcdefghijk"', repaired)
        self.assertNotIn("private/sources/", repaired)
        self.assertNotIn("npm run", repaired)
        self.assertIn("#ephesians_1_5-6", repaired)
        self.assertIn("(`source_id`: `youtube:abcdefghijk`)", repaired)
        repaired_again, second_report = repair_text(repaired, {"abcdefghijk"})
        self.assertEqual(repaired_again, repaired)
        self.assertEqual(second_report["changed"], 0)


if __name__ == "__main__":
    unittest.main()
