#!/usr/bin/env python3
"""Manual TTS smoke check — plays one synthesized phrase through the speakers.

Requires the Piper model downloaded (see README Setup) and real audio
hardware, so this is not part of the pytest suite. Run directly:

    python3 scripts/manual_test_tts.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.tts.engine import TTSEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")


def main() -> None:
    tts = TTSEngine()
    text = "Dzień dobry! Test systemu głosowego zakończony sukcesem. W czym mogę pomóc?"
    logging.info("speaking: %s", text)
    tts.speak_wait(text)
    logging.info("done")


if __name__ == "__main__":
    main()
