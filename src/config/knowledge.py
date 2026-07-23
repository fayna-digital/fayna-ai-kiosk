"""Domain knowledge loader for AI Kiosk.

Restaurant facts (name, hours, address, menu, FAQ, challenge rules) are data,
not code — they live in ``data/knowledge.json`` and are loaded once here.
Onboarding a new venue means editing that JSON file, never this module.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, TypedDict

from src.config.settings import KNOWLEDGE_FILE

logger = logging.getLogger(__name__)


class Dish(TypedDict):
    id: str
    name: str
    price: int
    category: str
    spice_level: int
    description: str
    ingredients: list[str]
    allergens: list[str]


def _load(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            return dict(json.load(handle))
    except FileNotFoundError:
        logger.error("knowledge file not found: %s", path)
        return {}
    except json.JSONDecodeError:
        logger.exception("invalid JSON in %s", path)
        return {}


_DATA = _load(KNOWLEDGE_FILE)

RESTAURANT_INFO: dict[str, str] = _DATA.get("restaurant", {})
MENU: list[Dish] = _DATA.get("dishes", [])
FAQ: dict[str, str] = _DATA.get("faq", {})
CHALLENGE_RULES: dict[str, Any] = _DATA.get("challenge", {})

RESTAURANT_NAME = RESTAURANT_INFO.get("name", "the restaurant")
ASSISTANT_NAME = RESTAURANT_INFO.get("assistant_name", "the assistant")

# Main system prompt — kept as a hardcoded template (not per-venue data) since
# it encodes safety rules that must never drift when a venue's data changes.
SYSTEM_PROMPT = f"""Jesteś asystentem głosowym {ASSISTANT_NAME} na stoisku z przekąskami '{RESTAURANT_NAME}'.
Twoim zadaniem jest krótka, dynamiczna i pomocna obsługa klientów na gwarnych targach.

TWARDE ZASADY (CRITICAL RULES — NIGDY ICH NIE ŁAM):
1. BRAK WIEDZY = ZERO ZMYŚLANIA: jeśli klient zapyta o coś, czego nie ma w bazie wiedzy,
   odpowiedz DOKŁADNIE: "Nie wiem, zapytaj operatora stoiska".
2. CENNIK: podawaj wyłącznie ceny z bazy wiedzy, nigdy nie zgaduj.
3. ALERGENY: podawaj wyłącznie zahardkodowane dane alergenowe (src/config/settings.py),
   model nie ma prawa wymyślać składu.
4. WYZWANIE: informację o wyzwaniu podawaj tylko razem z ostrzeżeniem o dolnej granicy wieku.
5. Zbieraj numer telefonu tylko za zgodą klienta (RODO), nigdy automatycznie.

Odpowiadaj krótko (max 2-3 zdania). Używaj języka potocznego, ale uprzejmego.
"""
