#!/usr/bin/env python3
import unittest

from normalize_verse_tags import normalize_names, normalize_tags
from verse_tag_conventions import canonicalize_tag


class NormalizeVerseTagsTests(unittest.TestCase):
    def test_canonicalizes_spanish_book_slugs(self) -> None:
        text = "#iojanan_10_11 #ieshaiahu_53_5 #ephesians_2_14-16 #2reyes_22_8"
        normalized, count, _ = normalize_tags(text)
        self.assertEqual(
            normalized,
            "#juan_10_11 #isaias_53_5 #efesios_2_14-16 #2_reyes_22_8",
        )
        self.assertEqual(count, 4)

    def test_keeps_unknown_non_scriptural_tags(self) -> None:
        text = "#tema #berajot_2a #iojanan_10_11"
        normalized, count, _ = normalize_tags(text)
        self.assertEqual(normalized, "#tema #berajot_2a #juan_10_11")
        self.assertEqual(count, 1)

    def test_normalizes_yod_names_in_prose(self) -> None:
        normalized, count = normalize_names("Iaakov habló con Ieshaiahu e Iojanán.")
        self.assertEqual(normalized, "Yaakov habló con Yeshayahu e Yojanán.")
        self.assertEqual(count, 3)

    def test_normalizes_visible_table_text(self) -> None:
        text = "| #iojanan_10_11 | Iojanán / Iaacob |\n"
        normalized, count = normalize_names(text)
        self.assertEqual(normalized, "| #iojanan_10_11 | Yojanán / Yaakov |\n")
        self.assertEqual(count, 2)

    def test_aliases_are_canonical(self) -> None:
        self.assertEqual(canonicalize_tag("#galatians_3_13"), "#galatas_3_13")
        self.assertEqual(canonicalize_tag("#shemuel_2_12_1-15"), "#2_samuel_12_1-15")
        self.assertEqual(canonicalize_tag("#iojanan_7_53-8_11"), "#juan_7_53-8_11")


if __name__ == "__main__":
    unittest.main()
