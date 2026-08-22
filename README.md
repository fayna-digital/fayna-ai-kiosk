# AI Kiosk — Offline'owy Asystent Głosowy dla Punktu Obsługi

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![STT](https://img.shields.io/badge/STT-Vosk%20Offline-red)
![TTS](https://img.shields.io/badge/TTS-Piper%20Neural-red)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/status-demo%20%2F%20portfolio-orange)

**Opracowane przez [Fayna Digital](https://fayna.agency) — Autor: Volodymyr Shevchenko**

---

Autonomiczny kiosk głosowy dla targów i małych punktów obsługi: nasłuchuje
polskiej mowy, rozumie naturalne pytania o menu, ceny i promocje, a odpowiada
neuralnym głosem — **w 100% offline**, bez API chmurowych i bez abonamentu.

> ⚠️ **Konfiguracja demo.** Repozytorium zawiera dane dla **fikcyjnego**
> ormiańskiego baru przekąskowego „Bar Przykład" (`przykład` = po polsku
> „example") — każda nazwa, adres, numer telefonu i danie są zmyślone.
> Wdrożenie realnego punktu polega tylko na edycji `data/knowledge.json` — bez
> zmian w kodzie. Prawdziwe dane klienta (nagrania rozmów, realne menu,
> kontakty) nigdy nie znajdują się w tym repozytorium.

## Kluczowe funkcje

| Funkcja | Implementacja |
|---|---|
| Offline'owe rozpoznawanie mowy | [Vosk](https://alphacephei.com/vosk/) z polskim modelem językowym |
| Offline'owa neuronowa synteza mowy | [Piper TTS](https://github.com/rhasspy/piper) — model VITS `pl_PL-gosia-medium`, bez internetu |
| Silnik NLP | Deterministyczny dopasowywacz słów kluczowych po `data/knowledge.json` (zero halucynacji) |
| UI | Pełnoekranowy tryb kiosku Tkinter (bez zależności od przeglądarki) |
| Reguły biznesowe | Zahardkodowane dane alergenów, walidacja wieku, tematy zabronione — model nie może wymyślać odpowiedzi |
| Pętla promocyjna | Wątek w tle odtwarza losowe promocje między interakcjami |
| Dialog ciągły | Rozmowa wieloetapowa — kilka pytań w jednej sesji |

## Architektura

```
┌─────────────────────────────────────────────────┐
│                  VoiceKioskApp                   │
│  ┌──────────┐  ┌────────────┐  ┌─────────────┐  │
│  │ STTEngine│  │NLPProcessor│  │  TTSEngine  │  │
│  │  (Vosk)  │→ │ (keywords) │→ │  (Piper)    │  │
│  └──────────┘  └────────────┘  └─────────────┘  │
│                                                  │
│  Tryby: PROMO ←→ DIALOG                          │
│  PROMO: pętla promocyjna w tle (TTS co 15 s)     │
│  DIALOG: słuchaj → dopasuj → mów → pętla         │
└─────────────────────────────────────────────────┘
```

**Przebieg dialogu:**
1. Gość naciska START.
2. Kiosk mówi: *„Słucham, w czym mogę pomóc?"*
3. STT nasłuchuje → Vosk transkrybuje polską mowę.
4. NLP dopasowuje słowa kluczowe do `data/knowledge.json` → deterministyczna odpowiedź (bez LLM).
5. TTS odtwarza odpowiedź przez Piper → `afplay` (macOS) / `aplay` (Linux).
6. Pętla wraca do trybu nasłuchu.

## Struktura projektu

```
├── src/
│   ├── main.py                 # Wejście aplikacji, pętla kiosku
│   ├── stt_engine.py           # Rozpoznawanie mowy (Vosk)
│   ├── nlp_processor.py        # Dopasowywanie intencji (słowa kluczowe)
│   ├── tts_engine.py           # Synteza mowy (Piper)
│   ├── config/settings.py      # Reguły krytyczne dla bezpieczeństwa
│   └── assets/models/          # Modele Vosk + Piper (pobierane)
├── tests/
│   ├── test_stt.py             # Testy rozpoznawania mowy
│   ├── test_nlp.py             # Testy silnika NLP
│   └── test_tts.py             # Ręczna kontrola głośnika (wymaga sprzętu)
├── scripts/
│   ├── install-kiosk.sh        # Instalator usługi systemd (Linux/Raspberry Pi)
│   └── ai-kiosk.service        # Plik jednostki systemd
├── docs/
│   └── 01_architecture_decisions.md
├── data/
│   └── knowledge.json          # Jedno źródło prawdy: punkt, menu, FAQ
├── index.html                  # Statyczna strona menu (bez serwera)
└── requirements.txt
```

## Instalacja

### Wymagania

- **Python 3.11** (wymagany — `piper-tts` zależy od `onnxruntime`, który nie ma jeszcze wheeli dla Pythona 3.13+)
- macOS (`afplay`) lub Linux (`aplay` z `alsa-utils`)
- Mikrofon

### Instalacja

```bash
git clone https://github.com/fayna-digital/fayna-ai-kiosk.git
cd fayna-ai-kiosk

# macOS: zainstaluj Python 3.11, jeśli potrzeba
brew install python@3.11 espeak-ng

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Pobranie polskiego modelu Vosk (STT)

```bash
mkdir -p src/assets/models/vosk-model-pl
curl -L https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip -o vosk.zip
unzip vosk.zip -d src/assets/models/
mv src/assets/models/vosk-model-small-pl-0.22 src/assets/models/vosk-model-pl
rm vosk.zip
```

### Pobranie polskiego modelu głosu Piper (TTS)

```bash
mkdir -p src/assets/models/piper
curl -L -o src/assets/models/piper/pl_PL-gosia-medium.onnx \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx"
curl -L -o src/assets/models/piper/pl_PL-gosia-medium.onnx.json \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx.json"
```

> Rozmiar modelu: ~60 MB. Alternatywny głos (męski): zamień `gosia` na `mc_speech`.

### Uruchomienie

```bash
source venv/bin/activate
python3 -m src.main
```

Testy:

```bash
python3 -m pytest tests/ -v
```

## Konfiguracja

Dwie warstwy, celowo rozdzielone:

- **`data/knowledge.json`** — wszystko, co dotyczy punktu: nazwa, godziny,
  adres, telefon, menu, FAQ, zasady wyzwania. Wdrożenie nowego punktu oznacza
  edycję tylko tego pliku.
- **`src/config/settings.py`** — reguły krytyczne dla bezpieczeństwa, których
  model nigdy nie może wnioskować: zahardkodowana tabela alergenów, minimalny
  wiek do wyzwania degustacyjnego, tematy zabronione, strojenie audio/UI.

```python
FULLSCREEN_MODE = True      # Blokada pełnoekranowa (tryb kiosku)
HIDE_CURSOR = True          # Ukrycie kursora myszy
NOISE_GATE_THRESHOLD = 500  # Dostrojenie do hałasu otoczenia
ENABLE_BARGE_IN = True      # Gość może przerwać odtwarzanie TTS
MIN_AGE_RECORD = 16         # Ograniczenie wieku wyzwania (zahardkodowane)
UNKNOWN_RESPONSE = "Nie znam odpowiedzi, zapytaj operatora."
```

Dane alergenów są **zahardkodowane** (nie generowane przez AI), aby zapobiec
halucynacjom — patrz [docs/01_architecture_decisions.md](docs/01_architecture_decisions.md).

## NLP — Obsługiwane intencje

Silnik słów kluczowych pokrywa 15+ kategorii intencji, wszystkie odpowiadane
z `data/knowledge.json`:

| Intencja | Przykładowe pytanie | Odpowiedź |
|---|---|---|
| Powitanie | *cześć, hej* | Wiadomość powitalna |
| Lista menu | *co macie, jakie smaki* | Pełne menu z ceną |
| Cena | *ile kosztuje, cena* | Cena za pozycję |
| Co to za wypiek | *co to jest* | Opis produktu |
| Rekomendacja | *co polecasz, co wziąć* | Sugestia na podstawie smaku |
| Ostre/łagodne | *ostre, pikantne* | Przewodnik po poziomie ostrości |
| Dla dzieci | *dla dzieci, dziecko* | Bezpieczna rekomendacja |
| Alergeny | *alergen, gluten, orzechy* | Zahardkodowana bezpieczna odpowiedź |
| Godziny otwarcia | *godziny, otwarte* | Z danych punktu |
| Adres | *gdzie, adres, ulica* | Z danych punktu |
| Dostawa | *dowóz, dostawa* | Informacje o dostawie |
| Wyzwanie | *wyzwanie, rekord* | Zasady + ostrzeżenie o wieku |
| Pożegnanie | *dziękuję, do widzenia* | Pożegnanie + koniec sesji |

## Wdrożenie (Linux / Raspberry Pi)

```bash
sudo bash scripts/install-kiosk.sh
sudo systemctl status ai-kiosk
journalctl -u ai-kiosk -f
```

Usługa automatycznie restartuje się po awarii i startuje przy starcie systemu.

## Decyzje architektoniczne

Patrz [docs/01_architecture_decisions.md](docs/01_architecture_decisions.md) po pełny ADR obejmujący:
- Dlaczego offline'owy STT (Vosk) zamiast chmury (Google/Whisper)
- Dlaczego deterministyczne NLP zamiast LLM
- Dlaczego Piper TTS zamiast zależnych od chmury alternatyw
- Strategia bramki szumów dla środowisk targowych
- Zgodne z GDPR/RODO, opcjonalne zbieranie leadów

## Kontekst biznesowy

**Przypadek użycia:** obsługa klienta bez użycia rąk na ruchliwym targu lub
stoisku. **Rozwiązany problem:** personel nie może jednocześnie obsługiwać
klientów i odpowiadać na powtarzalne pytania. **Efekt:** autonomicznie obsługuje
ruch FAQ, uwalniając personel do sprzedaży. Ten silnik został wyodrębniony
i zanonimizowany z realnego wdrożenia klienckiego procedurą Project Sunset
Fayna — patrz [CHANGELOG.md](CHANGELOG.md).

## Licencja

MIT — patrz [LICENSE](LICENSE). © Fayna Digital.

## Wykonane przez

**Fayna Digital** — agencja architektury systemów i automatyzacji AI
[fayna.agency](https://fayna.agency) · [github.com/fayna-digital](https://github.com/fayna-digital)

> Core Tech: Python 3.11 · Vosk · Piper TTS · Tkinter · architektura w 100% offline
