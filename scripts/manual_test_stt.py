#!/usr/bin/env python3
"""Manual STT smoke check — records 10 seconds from the microphone and prints
what Vosk recognized.

Requires the Vosk model downloaded (see README Setup) and a real microphone,
so this is not part of the pytest suite. Run directly:

    python3 scripts/manual_test_stt.py
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.stt.engine import STTEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

LISTEN_SECONDS = 10


def main() -> None:
    stt = STTEngine()
    stt.start_listening()
    logging.info("listening for %ss — speak into the microphone now", LISTEN_SECONDS)

    start_time = time.time()
    try:
        while time.time() - start_time < LISTEN_SECONDS:
            text = stt.get_text(block=False)
            if text:
                logging.info("recognized: %s", text)
            time.sleep(0.2)
    finally:
        stt.stop_listening()
    logging.info("done")


if __name__ == "__main__":
    main()
