"""Deterministic, keyword-based NLP over the venue's knowledge base.

A kiosk must never invent a price, an ingredient or an allergen, so every
answer is matched against ``data/knowledge.json`` (loaded via
:mod:`src.config.knowledge`) rather than generated. Order matters: more
specific keyword groups are checked before general ones.
"""

from __future__ import annotations

from src.config.knowledge import CHALLENGE_RULES, FAQ, MENU, RESTAURANT_INFO, RESTAURANT_NAME
from src.config.settings import UNKNOWN_RESPONSE

_GREETING_KEYWORDS = ("cześć", "czesc", "hej", "dzień dobry", "dzien dobry", "dobry wieczór", "dobry wieczor")
_MENU_KEYWORDS = ("menu", "co macie", "jakie smaki", "co jest", "lista")
_PRICE_KEYWORDS = ("cena", "ile kosztuje", "ile kosztują", "cennik", "ile płacę", "ile to kosztuje")
_WHAT_IS_KEYWORDS = ("co to jest", "co to pasztecik", "czym jest", "co to")
_RECOMMEND_KEYWORDS = (
    "polecacie",
    "polecasz",
    "co polecasz",
    "co wziąć",
    "co wziac",
    "co wybrać",
    "co wybrac",
)
_CHILDREN_KEYWORDS = ("dziecko", "dzieci", "dla dzieci", "dziecku")
_SPICY_KEYWORDS = ("ostre", "ostry", "pikantne", "pikantny", "ostrość", "ostrosc")
_SWEET_KEYWORDS = ("słodkie", "slodkie", "słodki", "slodki", "deser")
_SAUCE_KEYWORDS = ("sosy", "sos", "do sosu", "jaki sos")
_ALLERGEN_KEYWORDS = ("alergen", "alergeny", "gluten", "orzechy", "jaja", "alergia")
_CALORIE_KEYWORDS = ("kalorie", "kcal", "dieta", "kaloryczny", "ile kalorii")
_HOURS_KEYWORDS = (
    "godziny",
    "kiedy",
    "otwarcie",
    "zamknięcie",
    "zamkniecie",
    "otwarte",
    "do kiedy",
    "od kiedy",
)
_ADDRESS_KEYWORDS = (
    "adres",
    "gdzie",
    "ulica",
    "lokalizacja",
    "gdzie jesteście",
    "gdzie jestescie",
    "dojazd",
)
_DELIVERY_KEYWORDS = ("dowóz", "dowoz", "dostawa", "dowoźcie", "dowozicie", "na wynos")
_CHALLENGE_KEYWORDS = ("rekord", "wyzwan", "konkurs")
_GOODBYE_KEYWORDS = ("dziękuję", "dziekuje", "dzieki", "dzięki", "do widzenia", "pa", "na razie")


class NLPProcessor:
    """Answer visitor questions from the loaded knowledge base."""

    def get_response(self, text: str) -> str:
        query = text.lower().strip()

        for keyword, answer in FAQ.items():
            if keyword in query:
                return answer

        if any(kw in query for kw in _GREETING_KEYWORDS):
            return f"Cześć! Witaj w {RESTAURANT_NAME}! W czym mogę Ci pomóc?"

        if any(kw in query for kw in _MENU_KEYWORDS):
            return self.get_all_menu()

        if any(kw in query for kw in _PRICE_KEYWORDS):
            price = MENU[0]["price"] if MENU else "?"
            return f"Każdy pasztecik kosztuje tylko {price} złotych. Dowóz to 10 zł."

        if any(kw in query for kw in _WHAT_IS_KEYWORDS):
            return (
                "Pasztecik to ormiańska przekąska — ciasto z jogurtu, mąki i jajek, "
                "smażone na głębokim oleju. Podajemy na ciepło!"
            )

        if any(kw in query for kw in _RECOMMEND_KEYWORDS):
            return FAQ.get(
                "polecacie",
                "Polecam nasz łagodniejszy pasztecik dla początkujących i ostrzejszy dla odważnych!",
            )

        if any(kw in query for kw in _CHILDREN_KEYWORDS):
            mildest = self._extreme_dish(spiciest=False)
            if not mildest:
                return UNKNOWN_RESPONSE
            return f"Dla dzieci polecam {mildest} — najłagodniejszy i najbardziej aromatyczny!"

        if any(kw in query for kw in _SPICY_KEYWORDS):
            return self._spice_summary()

        if any(kw in query for kw in _SWEET_KEYWORDS):
            sweets = [dish["name"] for dish in MENU if dish["spice_level"] == 0]
            if not sweets:
                return UNKNOWN_RESPONSE
            return f"Mamy słodkie smaki: {', '.join(sweets)}. Wszystkie za 8 zł!"

        if any(kw in query for kw in _SAUCE_KEYWORDS):
            return RESTAURANT_INFO.get("sauces", UNKNOWN_RESPONSE)

        if any(kw in query for kw in _ALLERGEN_KEYWORDS):
            return (
                "Ciasto zawiera gluten i jaja. Pasztecik z nutellą zawiera również orzechy. "
                "Brak opcji wegańskich — wszystkie smaki słone są wegetariańskie."
            )

        if any(kw in query for kw in _CALORIE_KEYWORDS):
            return "Od 220 do 270 kcal, zależnie od smaku. Dokładne info u obsługi stoiska."

        if any(kw in query for kw in _HOURS_KEYWORDS):
            return RESTAURANT_INFO.get("hours", UNKNOWN_RESPONSE)

        if any(kw in query for kw in _ADDRESS_KEYWORDS):
            address = RESTAURANT_INFO.get("address", "")
            phone = RESTAURANT_INFO.get("phone", "")
            return f"Znajdziesz nas przy {address} Telefon: {phone}.".strip()

        if any(kw in query for kw in _DELIVERY_KEYWORDS):
            return RESTAURANT_INFO.get("delivery", UNKNOWN_RESPONSE)

        if any(kw in query for kw in _CHALLENGE_KEYWORDS):
            return self._challenge_summary()

        if any(kw in query for kw in _GOODBYE_KEYWORDS):
            return "Dziękuję i zapraszam ponownie! Smacznego!"

        return UNKNOWN_RESPONSE

    @staticmethod
    def get_all_menu() -> str:
        if not MENU:
            return "Menu jest chwilowo niedostępne."
        names = ", ".join(dish["name"] for dish in MENU)
        price = MENU[0]["price"]
        return f"Mamy {len(MENU)} smaków: {names}. Każdy kosztuje tylko {price} zł!"

    @staticmethod
    def _extreme_dish(*, spiciest: bool) -> str | None:
        """Hottest/mildest *savory* dish — spice level is not meaningful for sweets."""
        savory = [dish for dish in MENU if dish["category"] == "słony"]
        if not savory:
            return None
        picker = max if spiciest else min
        dish = picker(savory, key=lambda d: d["spice_level"])
        return str(dish["name"])

    @classmethod
    def _spice_summary(cls) -> str:
        hottest = cls._extreme_dish(spiciest=True)
        mildest = cls._extreme_dish(spiciest=False)
        if not hottest or not mildest:
            return UNKNOWN_RESPONSE
        return f"Najostrzejszy to {hottest}. Zupełnie łagodny: {mildest}."

    @staticmethod
    def _challenge_summary() -> str:
        if not CHALLENGE_RULES:
            return UNKNOWN_RESPONSE
        name = CHALLENGE_RULES.get("name", "Wyzwanie")
        goal = CHALLENGE_RULES.get("goal", "")
        min_age = CHALLENGE_RULES.get("min_age", 16)
        return f"{name}: {goal} Trzeba mieć min. {min_age} lat. Zgłoszenia dzień wcześniej."
