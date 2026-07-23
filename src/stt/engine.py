"""Offline speech-to-text engine (Vosk + PyAudio, Polish model)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pyaudio
from vosk import KaldiRecognizer, Model

logger = logging.getLogger(__name__)

MODEL_PATH = Path("src/assets/models/vosk-model-pl")
SAMPLE_RATE = 16000
CHUNK_SIZE = 4000


def parse_vosk_result(raw_result: str) -> str | None:
    """Extract the recognized text from a Vosk JSON result string, or None."""
    try:
        data = json.loads(raw_result)
    except json.JSONDecodeError:
        logger.warning("could not parse Vosk result as JSON: %r", raw_result)
        return None
    text = data.get("text")
    return text or None


class STTEngine:
    """Wraps Vosk + PyAudio for offline Polish speech recognition."""

    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        self._model = Model(str(model_path))
        self._recognizer = KaldiRecognizer(self._model, SAMPLE_RATE)
        self._audio = pyaudio.PyAudio()
        self._stream: pyaudio.Stream | None = None

    def start_listening(self) -> None:
        self._stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )
        self._stream.start_stream()

    def get_text(self, block: bool = True) -> str | None:
        """Read one chunk of audio and return recognized text, if any.

        ``block`` is accepted for API symmetry with callers that poll in a
        loop; PyAudio's ``read()`` always blocks for the requested chunk, so
        both modes behave the same here — there is no non-blocking backend.
        """
        del block  # accepted for interface symmetry, see docstring
        if self._stream is None:
            return None
        try:
            data = self._stream.read(CHUNK_SIZE // 2, exception_on_overflow=False)
        except OSError:
            logger.exception("audio stream read failed")
            return None
        if self._recognizer.AcceptWaveform(data):
            return parse_vosk_result(self._recognizer.Result())
        return None

    def stop_listening(self) -> None:
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
