#!/usr/bin/env python3
import unittest

from check_verse_tag_conventions import ROOT
from normalize_verse_tags import normalize_names, normalize_tags


class CheckVerseTagConventionsTests(unittest.TestCase):
    def test_migration_is_idempotent_for_canonical_content(self) -> None:
        text = "#iojanan_10_11 y Ieshaiahu; no Iaakov."
        normalized_tags, _, _ = normalize_tags(text)
        normalized_names, _ = normalize_names(normalized_tags)
        self.assertEqual(normalized_names, "#juan_10_11 y Yeshayahu; no Yaakov.")
        second, _ = normalize_names(normalized_names)
        self.assertEqual(second, normalized_names)

    def test_root_is_repository_root(self) -> None:
        self.assertTrue((ROOT / "content").is_dir())


if __name__ == "__main__":
    unittest.main()
