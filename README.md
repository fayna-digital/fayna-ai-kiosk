# AI Kiosk — Offline Voice Assistant for Point of Sale

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![STT](https://img.shields.io/badge/STT-Vosk%20Offline-red)
![TTS](https://img.shields.io/badge/TTS-Piper%20Neural-red)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/status-demo%20%2F%20portfolio-orange)

**Developed by [Fayna Digital](https://fayna.agency) — Author: Volodymyr Shevchenko**

---

An autonomous voice-driven kiosk for trade fairs and small venues: it listens
for Polish speech, understands natural questions about a menu, prices and
promotions, and answers with a neural voice — **100% offline**, no cloud APIs,
no ongoing subscription cost.

> ⚠️ **Demo configuration.** The repository ships with data for a **fictional**
> Armenian snack bar, "Bar Przykład" (`przykład` = Polish for "example") — every
> name, address, phone number and dish is made up. Onboarding a real venue only
> means editing `data/knowledge.json` — no code changes required. Real client
> data (conversation recordings, an actual menu, contacts) never lives in this
> repository.

## Key Features

| Feature | Implementation |
|---|---|
| Offline Speech Recognition | [Vosk](https://alphacephei.com/vosk/) with a Polish language model |
| Offline Neural Text-to-Speech | [Piper TTS](https://github.com/rhasspy/piper) — VITS model `pl_PL-gosia-medium`, no internet required |
| NLP Engine | Deterministic rule-based keyword matcher over `data/knowledge.json` (zero hallucinations) |
| UI | Tkinter fullscreen kiosk mode (no browser dependency) |
| Business Rules | Hardcoded allergen data, age validation, forbidden topics — the model cannot invent answers |
| Promo Loop | Background thread plays random promotions between interactions |
| Continuous Dialog | Multi-turn conversation — several questions per session |

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  VoiceKioskApp                   │
│  ┌──────────┐  ┌────────────┐  ┌─────────────┐  │
│  │ STTEngine│  │NLPProcessor│  │  TTSEngine  │  │
│  │  (Vosk)  │→ │ (keywords) │→ │  (Piper)    │  │
│  └──────────┘  └────────────┘  └─────────────┘  │
│                                                  │
│  Modes: PROMO ←→ DIALOG                          │
│  PROMO: background promo loop (TTS every 15s)    │
│  DIALOG: listen → match → speak → loop           │
└─────────────────────────────────────────────────┘
```

**Dialog flow:**
1. Visitor presses START.
2. Kiosk says: *"Słucham, w czym mogę pomóc?"*
3. STT listens → Vosk transcribes Polish speech.
4. NLP matches keywords against `data/knowledge.json` → deterministic response (no LLM).
5. TTS speaks the response via Piper → `afplay` (macOS) / `aplay` (Linux).
6. Loop continues until: goodbye phrase detected, 15s inactivity, or STOP pressed.

## Project Structure

```
ai-kiosk/
├── src/
│   ├── main.py                  # Entry point — VoiceKioskApp (Tkinter)
│   ├── config/
│   │   ├── settings.py          # Safety-critical rules: allergens, age limits
│   │   └── knowledge.py         # Loads data/knowledge.json (per-venue facts)
│   ├── nlp/
│   │   └── processor.py         # Keyword-based NLP — 15+ intent categories
│   ├── stt/
│   │   └── engine.py            # Vosk offline STT engine (Polish)
│   ├── tts/
│   │   └── engine.py            # Piper neural TTS engine
│   └── kiosk/
│       └── kiosk_mode.py        # Optional Chromium companion display (Linux)
├── tests/
│   └── test_nlp.py              # Unit tests — no audio hardware needed
├── scripts/
│   ├── manual_test_stt.py       # Manual mic check (needs hardware)
│   ├── manual_test_tts.py       # Manual speaker check (needs hardware)
│   ├── install-kiosk.sh         # systemd service installer (Linux/Raspberry Pi)
│   └── ai-kiosk.service         # systemd unit file
├── docs/
│   └── 01_architecture_decisions.md
├── data/
│   └── knowledge.json           # Single source of truth: venue, menu, FAQ
├── index.html                   # Static web menu page (no server needed)
└── requirements.txt
```

## Setup

### Requirements

- **Python 3.11** (required — `piper-tts` depends on `onnxruntime`, which has no Python 3.13+ wheels yet)
- macOS (`afplay`) or Linux (`aplay` from `alsa-utils`)
- Microphone

### Install

```bash
git clone https://github.com/fayna-digital/ai-kiosk.git
cd ai-kiosk

# macOS: install Python 3.11 if needed
brew install python@3.11 espeak-ng

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Download the Vosk Polish model (STT)

```bash
mkdir -p src/assets/models/vosk-model-pl
curl -L https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip -o vosk.zip
unzip vosk.zip -d src/assets/models/
mv src/assets/models/vosk-model-small-pl-0.22 src/assets/models/vosk-model-pl
rm vosk.zip
```

### Download the Piper Polish voice model (TTS)

```bash
mkdir -p src/assets/models/piper
curl -L -o src/assets/models/piper/pl_PL-gosia-medium.onnx \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx"
curl -L -o src/assets/models/piper/pl_PL-gosia-medium.onnx.json \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx.json"
```

> Model size: ~60 MB. Alternative voice (male): replace `gosia` with `mc_speech`.

### Run

```bash
source venv/bin/activate
python3 -m src.main
```

Tests:

```bash
python3 -m pytest tests/ -v
```

## Configuration

Two layers, deliberately kept apart:

- **`data/knowledge.json`** — everything specific to a venue: name, hours,
  address, phone, menu, FAQ, challenge rules. Onboarding a new venue means
  editing this file only.
- **`src/config/settings.py`** — safety-critical rules that must never be
  inferred by a model: hardcoded allergen table, minimum age for the tasting
  challenge, forbidden topics, audio/UI tuning.

```python
FULLSCREEN_MODE = True      # Lock to fullscreen (kiosk mode)
HIDE_CURSOR = True          # Hide the mouse cursor
NOISE_GATE_THRESHOLD = 500  # Adjust for venue ambient noise
ENABLE_BARGE_IN = True      # Visitor can interrupt TTS playback
MIN_AGE_RECORD = 16         # Tasting-challenge age restriction (hardcoded)
UNKNOWN_RESPONSE = "Nie znam odpowiedzi, zapytaj operatora."
```

Allergen data is **hardcoded** (not AI-generated) to prevent hallucinations —
see [docs/01_architecture_decisions.md](docs/01_architecture_decisions.md).

## NLP — Supported Intents

The keyword engine covers 15+ intent categories, all answered from `data/knowledge.json`:

| Intent | Example query | Response |
|---|---|---|
| Greeting | *cześć, hej* | Welcome message |
| Menu list | *co macie, jakie smaki* | Full menu with price |
| Price | *ile kosztuje, cena* | Price per item |
| What is a pastry | *co to jest* | Product description |
| Recommendation | *co polecasz, co wziąć* | Taste-based suggestion |
| Spicy/mild | *ostre, pikantne* | Spice-level guide |
| Children | *dla dzieci, dziecko* | Safe recommendation |
| Allergens | *alergen, gluten, orzechy* | Hardcoded safe answer |
| Opening hours | *godziny, otwarte* | From venue data |
| Address | *gdzie, adres, ulica* | From venue data |
| Delivery | *dowóz, dostawa* | Delivery info |
| Challenge | *wyzwanie, rekord* | Rules + age warning |
| Goodbye | *dziękuję, do widzenia* | Farewell + session end |

## Deployment (Linux / Raspberry Pi)

```bash
sudo bash scripts/install-kiosk.sh
sudo systemctl status ai-kiosk
journalctl -u ai-kiosk -f
```

The service auto-restarts on failure and starts at boot.

## Architecture Decisions

See [docs/01_architecture_decisions.md](docs/01_architecture_decisions.md) for the full ADR covering:
- Why offline STT (Vosk) over cloud (Google/Whisper)
- Why deterministic NLP over an LLM
- Why Piper TTS over cloud-dependent alternatives
- Noise-gate strategy for trade-fair environments
- GDPR/RODO-compliant, opt-in lead collection

## Business Context

**Use case:** hands-free customer service at a busy market or trade-fair stand.
**Problem solved:** staff cannot simultaneously serve customers and answer
repetitive questions.
**Result:** handles FAQ traffic autonomously, freeing staff for upselling.
This engine was extracted and anonymized from a real client deployment via
Fayna's Project Sunset procedure — see [CHANGELOG.md](CHANGELOG.md).

## License

MIT — see [LICENSE](LICENSE). © Fayna Digital.

## Built by

**Fayna Digital** — Systems architecture & AI automation agency
[fayna.agency](https://fayna.agency) · [github.com/fayna-digital](https://github.com/fayna-digital)

> Core Tech: Python 3.11 · Vosk · Piper TTS · Tkinter · 100% offline architecture
