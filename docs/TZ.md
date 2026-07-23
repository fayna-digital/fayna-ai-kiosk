# TZ — AI Kiosk

> Full checklist of implemented and planned functionality.
> ✅ — done | 🔲 — planned | ❌ — cancelled

---

## 1. Core

| Component | Technology | Status |
|-----------|-----------|--------|
| STT Engine | Vosk (offline, Polish model) | ✅ |
| TTS Engine | Piper VITS (`pl_PL-gosia-medium.onnx`) | ✅ |
| NLP Engine | Keyword-based (deterministic, 15+ intents) | ✅ |
| UI | Tkinter fullscreen kiosk | ✅ |
| Dialog modes | PROMO (background loop) + DIALOG (listen/respond) | ✅ |
| Multi-turn conversation | ✅ |
| Promo loop | Background TTS every 15s between interactions | ✅ |

---

## 2. STT (Speech-to-Text)

| Feature | Status |
|---------|--------|
| Offline Polish STT (Vosk `vosk-model-small-pl-0.22`) | ✅ |
| Noise gate (`NOISE_GATE_THRESHOLD = 500`) | ✅ |
| Automatic STT restart after each response | ✅ |
| 15-second inactivity timeout | ✅ |
| `ENABLE_BARGE_IN` — interrupt TTS playback | ✅ |
| Goodbye-phrase detection ends the session | ✅ |

---

## 3. TTS (Text-to-Speech)

| Feature | Status |
|---------|--------|
| Offline Piper TTS `pl_PL-gosia-medium` (female voice) | ✅ |
| Playback via `aplay` (Linux) / `afplay` (macOS) | ✅ |
| Greeting phrase: "Słucham, w czym mogę pomóc?" | ✅ |
| Goodbye phrase + session end | ✅ |

---

## 4. NLP — Supported Intents (15+)

| Intent | Example query | Status |
|--------|----------------|--------|
| Greeting | *cześć, hej, dzień dobry* | ✅ |
| Menu list | *co macie, jakie smaki* | ✅ |
| Price | *ile kosztuje, cena* | ✅ |
| What is a pastry | *co to jest* | ✅ |
| Recommendation | *co polecasz, co wziąć* | ✅ |
| Spicy/mild | *ostre, pikantne, łagodne* | ✅ |
| Children | *dla dzieci, dziecko* | ✅ |
| Allergens | *alergen, gluten, orzechy* | ✅ (hardcoded) |
| Opening hours | *godziny, otwarte, kiedy* | ✅ |
| Address | *gdzie, adres, ulica* | ✅ |
| Delivery | *dowóz, dostawa* | ✅ |
| Challenge | *wyzwanie, rekord, konkurs* | ✅ |
| Payment methods | *kartą, płacić* | ✅ (in venue data) |
| Goodbye | *dziękuję, do widzenia* | ✅ |

---

## 5. Knowledge Base

| Section | Status | Source |
|--------|--------|------|
| Menu with prices | ✅ | `data/knowledge.json` |
| Allergens (hardcoded, not AI) | ✅ | `src/config/settings.py` |
| Opening hours | ✅ | `data/knowledge.json` |
| Address / phone | ✅ | `data/knowledge.json` |
| Delivery terms | ✅ | `data/knowledge.json` |
| Challenge rules + minimum age (16+) | ✅ | `data/knowledge.json` + `src/config/settings.py` |
| `UNKNOWN_RESPONSE` fallback | ✅ | `src/config/settings.py` |

---

## 6. UI (Tkinter)

| Feature | Status |
|---------|--------|
| Fullscreen kiosk mode | ✅ |
| Hidden cursor | ✅ |
| START button | ✅ |
| STOP button | ✅ |
| Status line (listening / speaking / promo) | ✅ |
| Static web menu page (`index.html`) | ✅ |

---

## 7. Deployment & System Integration

| Feature | Status |
|---------|--------|
| `scripts/install-kiosk.sh` — systemd service installer | ✅ |
| `scripts/ai-kiosk.service` — unit file | ✅ |
| Auto-start on reboot | ✅ |
| Auto-restart on crash | ✅ |
| `run.sh` launcher | ✅ |
| Linux deployment (Ubuntu / Raspberry Pi OS) | ✅ |

---

## 8. Roadmap

| Feature | Status | Priority |
|---------|--------|-----------|
| Whisper STT (if hardware upgraded) | 🔲 | Medium |
| POS integration (live prices) | 🔲 | Low |
| Multilingual mode (Polish + Ukrainian) | 🔲 | Low |
| Web admin panel for menu updates | 🔲 | Low |
| Python 3.13 compatibility (onnxruntime wheels) | 🔲 | Tech debt |
| Tests — full `get_response` branch coverage | ✅ (baseline) | — |

---

## Business Context

- **Use case:** hands-free voice assistant for a trade-fair / small-venue snack stand.
- **Status:** production-proven engine, published here as a sanitized demo.
- **Metric:** handles FAQ traffic autonomously, frees staff for upselling.
