#!/usr/bin/env python3
"""Regression tests for local Scripture lookups."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lookup_verse  # noqa: E402


class LookupVerseTests(unittest.TestCase):
    def test_qohelet_raw_oe_fallback_uses_canonical_tag_alias(self) -> None:
        result = lookup_verse.lookup("#eclesiastes_7_1")

        self.assertEqual(result["tag"], "#eclesiastes_7_1")
        self.assertEqual(result["tth"], None)
        self.assertEqual(result["delitzsch"], None)
        self.assertEqual(result["oe"], "טוב שם מ/שמן טוב ו/יום ה/מות מ/יום הולד/ו")

    def test_qohelet_raw_oe_fallback_returns_none_for_missing_verse(self) -> None:
        self.assertIsNone(lookup_verse.lookup_oe("qohelet", 7, 999))


if __name__ == "__main__":
    unittest.main()
