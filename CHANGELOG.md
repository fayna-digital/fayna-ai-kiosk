# Changelog

Format — [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning — [SemVer](https://semver.org/).

## [0.1.0] — 2026-07-23

### Added
- Initial public extract of the **AI Kiosk** engine (offline STT / NLP / TTS / Tkinter UI).
- Demo dataset for a fictional Armenian snack bar, "Bar Przykład" (all data is fictional).
- Repository brought to Fayna **REPO_STANDARD**: README, LICENSE (MIT), CI, `.pre-commit-config.yaml`,
  `docs/`, `tests/`.
- `no-ai-signature` guard (pre-commit) — blocks AI attribution in code and commits.
- Unit tests for `NLPProcessor` that run without any audio hardware, including a regression
  guard that fails the build if the original client's brand name ever resurfaces.

### Changed
- Menu, FAQ and venue facts now live in a single `data/knowledge.json`, loaded by
  `src/config/knowledge.py` — previously the same facts were duplicated across three
  inconsistent files (`config/knowledge.py`, `data/menu.json`, `data/qa.json`) that had
  drifted out of sync with each other and with the code actually driving responses.
- `src/stt/engine.py`: restored the `STTEngine` class (Vosk + PyAudio) that a prior
  hotfix had accidentally deleted while patching JSON-parsing error handling; the safety
  net is kept as the `parse_vosk_result()` helper, now with real unit coverage.
- Removed the hardcoded product photo asset and its Pillow dependency; the kiosk UI now
  draws a generic placeholder panel instead of loading an image file.
- Full type hints, top-level imports, specific exceptions (no bare `except:`) across
  `src/`; run via `python -m src.main` with a package-root `conftest.py` instead of
  per-file `sys.path` hacks.
- Lead capture (`SAVE_LEADS`) is opt-in and off by default (RODO/GDPR).

### Notes
- Extracted from an internal client project via Fayna's **Project Sunset** procedure.
  Deliberately **not** carried over: client identity, real visitor conversation
  recordings (RODO), the original git history (AI co-author trailers), and machine-specific
  `pip freeze` output (replaced with a curated `requirements.txt`).
