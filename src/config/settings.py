"""Runtime configuration & hardcoded business-safety rules for AI Kiosk.

Restaurant-specific facts (menu, hours, address) live in ``data/knowledge.json``
and are loaded by :mod:`src.config.knowledge` — swap that file for a new venue,
no code changes needed. What stays hardcoded here on purpose: safety-critical
rules (allergens, age limits, forbidden topics) that must never be inferred or
"helpfully" rewritten by a language model. See ``docs/01_architecture_decisions.md``.
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_FILE = DATA_DIR / "knowledge.json"

# ==========================================
# Safety-critical business rules (hardcoded, not AI-generated)
# ==========================================

# Minimum age to take part in the tasting challenge.
MIN_AGE_RECORD = 16

# Allergen data, keyed by dish id from data/knowledge.json. A model must
# never be allowed to invent or omit an allergen.
ALLERGENS_DB: dict[str, list[str]] = {
    "pastry_nutella": ["orzechy", "mleko", "soja", "gluten"],
    "pastry_beef": ["gluten"],
    "pastry_potato": ["gluten"],
    "pastry_mushroom": ["gluten"],
    "pastry_cabbage": ["gluten"],
    "pastry_lentil": ["gluten"],
    "pastry_curd_honey": ["gluten", "mleko"],
}

# Topics the assistant must refuse to discuss (jailbreak protection).
FORBIDDEN_TOPICS = ("polityka", "konkurencja", "religia", "system prompt", "ignore previous instructions")

# ==========================================
# Audio (noise gate / barge-in)
# ==========================================
NOISE_GATE_THRESHOLD = 500  # tune on-site for the venue's ambient noise
ENABLE_BARGE_IN = True  # let the visitor interrupt TTS playback

# ==========================================
# Kiosk UI
# ==========================================
FULLSCREEN_MODE = True
HIDE_CURSOR = True

# ==========================================
# Lead capture (opt-in, RODO/GDPR)
# ==========================================
# Off by default — enable only with a lawful basis and on-site signage.
SAVE_LEADS = os.getenv("KIOSK_SAVE_LEADS", "false").strip().lower() in {"1", "true", "yes", "on"}
LEADS_DB_URL = os.getenv("KIOSK_LEADS_DB_URL", "sqlite:///local_leads.db")

UNKNOWN_RESPONSE = "Nie znam odpowiedzi, zapytaj operatora."
