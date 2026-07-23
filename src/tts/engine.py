"""Offline neural text-to-speech engine (Piper VITS, Polish voice)."""

from __future__ import annotations

import logging
import platform
import subprocess
import threading
import wave
from pathlib import Path

from piper.voice import PiperVoice

logger = logging.getLogger(__name__)

MODEL_PATH = Path("src/assets/models/piper/pl_PL-gosia-medium.onnx")
OUTPUT_FILE = Path("temp_tts.wav")


class TTSEngine:
    """Synthesizes speech locally with Piper and plays it via the OS player."""

    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        self._voice = PiperVoice.load(str(model_path))
        self._stop_event = threading.Event()
        self._play_process: subprocess.Popen[bytes] | None = None
        self._lock = threading.Lock()
        logger.info("Piper voice loaded: %s", model_path)

    def speak_wait(self, text: str) -> None:
        """Synthesize and play ``text``, blocking until playback finishes."""
        with self._lock:
            self._stop_event.clear()

            try:
                with wave.open(str(OUTPUT_FILE), "wb") as wav_file:
                    self._voice.synthesize_wav(text, wav_file)
            except OSError:
                logger.exception("TTS synthesis failed")
                return

            if self._stop_event.is_set():
                return

            self._play(OUTPUT_FILE)

    def _play(self, wav_path: Path) -> None:
        system = platform.system()
        player = {"Darwin": "afplay", "Linux": "aplay"}.get(system)
        if player is None:
            logger.warning("no known audio player for platform %s", system)
            return
        try:
            self._play_process = subprocess.Popen([player, str(wav_path)])
            self._play_process.wait()
        except FileNotFoundError:
            logger.error("audio player not found on PATH: %s", player)
        except OSError:
            logger.exception("audio playback failed")

    def stop(self) -> None:
        self._stop_event.set()
        if self._play_process is not None and self._play_process.poll() is None:
            self._play_process.terminate()
            self._play_process = None
