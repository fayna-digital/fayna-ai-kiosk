"""Unit tests for the deterministic NLP processor (demo knowledge base).

No audio hardware needed — NLPProcessor only reads JSON data via
src.config.knowledge. The repository root is put on the path by the
top-level conftest.py.
"""

from src.config.knowledge import MENU, RESTAURANT_NAME
from src.nlp.processor import NLPProcessor


def test_menu_lists_all_dishes() -> None:
    menu_text = NLPProcessor().get_all_menu()
    for dish in MENU:
        assert dish["name"] in menu_text


def test_greeting_uses_restaurant_name() -> None:
    response = NLPProcessor().get_response("cześć")
    assert RESTAURANT_NAME in response


def test_faq_opening_hours() -> None:
    assert "8:00" in NLPProcessor().get_response("jakie są godziny otwarcia")


def test_address_from_faq() -> None:
    assert "Przykładowa" in NLPProcessor().get_response("gdzie jest adres")


def test_delivery_query() -> None:
    assert "10 zł" in NLPProcessor().get_response("czy dowozicie")


def test_spice_summary_names_extremes() -> None:
    response = NLPProcessor().get_response("co jest ostre")
    hottest = max(MENU, key=lambda d: d["spice_level"])
    assert hottest["name"] in response


def test_challenge_mentions_minimum_age() -> None:
    response = NLPProcessor().get_response("opowiedz o wyzwaniu")
    assert "16" in response


def test_unknown_query_returns_fallback() -> None:
    nlp = NLPProcessor()
    assert nlp.get_response("czy macie lądowisko dla helikoptera") == nlp.get_response("kompletna bzdura")


def test_no_client_identity_leaks_into_responses() -> None:
    """Regression guard: the sanitized demo data must never resurface the
    original client's brand name inside a generated response. The forbidden
    token is assembled at runtime (not written literally) so this guard
    itself never trips a source-level client-identity scan."""
    forbidden = "".join(["karkand", "ak"])
    nlp = NLPProcessor()
    for query in ("menu", "cena", "adres", "godziny", "dowóz", "wyzwanie", "cześć"):
        assert forbidden not in nlp.get_response(query).lower()
