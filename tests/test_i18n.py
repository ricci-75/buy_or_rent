"""Tests for translations and formatting."""

from buy_or_rent.i18n import LANGUAGES, TRANSLATIONS, format_eur, format_percent, t


def test_all_languages_share_the_same_keys() -> None:
    """Every language defines exactly the same keys."""
    assert set(TRANSLATIONS) == set(LANGUAGES)
    assert TRANSLATIONS["fr"].keys() == TRANSLATIONS["en"].keys()


def test_translate_falls_back_to_french() -> None:
    """Unknown languages use French."""
    assert t("title", "de") == TRANSLATIONS["fr"]["title"]
    assert t("title", "en") == "Rent or buy?"


def test_format_eur() -> None:
    """Euro amounts follow each language convention."""
    assert format_eur(1234567.4, "fr") == "1 234 567 €"
    assert format_eur(1234567.6, "en") == "€1,234,568"
    assert format_eur(-1500, "fr") == "-1 500 €"
    assert format_eur(-1500, "en") == "-€1,500"


def test_format_percent() -> None:
    """Percentages follow each language decimal separator."""
    assert format_percent(0.3333, "fr") == "33,3 %"
    assert format_percent(0.3333, "en") == "33.3%"
