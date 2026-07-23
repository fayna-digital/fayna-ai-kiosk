"""AI Kiosk — Tkinter application entry point.

Run from the repository root:  python -m src.main
"""

from __future__ import annotations

import logging
import random
import threading
import time
import tkinter as tk

from src.config.knowledge import RESTAURANT_NAME
from src.config.settings import FULLSCREEN_MODE, HIDE_CURSOR
from src.nlp.processor import NLPProcessor
from src.stt.engine import STTEngine
from src.tts.engine import TTSEngine

logger = logging.getLogger(__name__)

_GOODBYE_KEYWORDS = ("dziękuję", "dziekuje", "dzięki", "dzieki", "do widzenia", "pa", "na razie")
_PROMO_INTERVAL_SECONDS = 15
_IDLE_TIMEOUT_SECONDS = 15


class VoiceKioskApp:
    """Fullscreen kiosk: background PROMO loop, tap-to-talk DIALOG mode."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        if FULLSCREEN_MODE:
            self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#f9a03f")
        if HIDE_CURSOR:
            self.root.config(cursor="none")

        self.tts = TTSEngine()
        self.stt = STTEngine()
        self.nlp = NLPProcessor()

        self.mode = "PROMO"
        self.last_interaction = time.time()
        self.stop_promo = threading.Event()

        self.promo_playlist = [
            f"{RESTAURANT_NAME} to zdrowsza alternatywa dla fastfoodów.",
            "Wszystkie paszteciki za osiem złotych!",
            "Sosy własnej produkcji są naprawdę bardzo dobre.",
        ]

        self._setup_ui()
        self.start_promo_thread()

    def _setup_ui(self) -> None:
        placeholder = tk.Canvas(self.root, width=700, height=450, bg="#f9a03f", highlightthickness=0)
        placeholder.pack(pady=20)
        placeholder.create_rectangle(50, 50, 650, 400, fill="white", outline="")
        placeholder.create_text(350, 225, text="PRODUCT PHOTO", font=("Arial", 28, "bold"), fill="#f9a03f")

        self.status_label = tk.Label(
            self.root,
            text="ZAPYTAJ MNIE O COKOLWIEK",
            font=("Arial", 24, "bold"),
            bg="#f9a03f",
            fg="white",
        )
        self.status_label.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=200, height=200, bg="#f9a03f", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.circle = self.canvas.create_oval(10, 10, 190, 190, fill="white", outline="")
        self.btn_text = self.canvas.create_text(
            100, 100, text="START", font=("Arial", 20, "bold"), fill="#f9a03f"
        )

        self.canvas.tag_bind(self.circle, "<Button-1>", lambda _e: self.toggle_mode())
        self.canvas.tag_bind(self.btn_text, "<Button-1>", lambda _e: self.toggle_mode())

    def toggle_mode(self) -> None:
        if self.mode == "PROMO":
            self.mode = "DIALOG"
            self.canvas.itemconfig(self.circle, fill="#ff4444")
            self.canvas.itemconfig(self.btn_text, text="STOP", fill="white")
            threading.Thread(target=self._dialog_session, daemon=True).start()
        else:
            self.mode = "PROMO"
            self._reset_ui()

    def _reset_ui(self) -> None:
        self.canvas.itemconfig(self.circle, fill="white")
        self.canvas.itemconfig(self.btn_text, text="START", fill="#f9a03f")
        self.status_label.config(text="ZAPYTAJ MNIE O COKOLWIEK")

    def _set_status(self, text: str) -> None:
        self.root.after(0, lambda: self.status_label.config(text=text))

    @staticmethod
    def _is_goodbye(text: str) -> bool:
        text_lower = text.lower()
        return any(kw in text_lower for kw in _GOODBYE_KEYWORDS)

    def start_promo_thread(self) -> None:
        def promo_loop() -> None:
            while not self.stop_promo.is_set():
                if self.mode == "PROMO":
                    msg = random.choice(self.promo_playlist)
                    self.tts.speak_wait(msg)
                    time.sleep(_PROMO_INTERVAL_SECONDS)
                time.sleep(1)

        threading.Thread(target=promo_loop, daemon=True).start()

    def _dialog_session(self) -> None:
        logger.info("dialog session started")
        try:
            self._set_status("MÓWIĘ...")
            self.tts.speak_wait("Słucham, w czym mogę pomóc?")

            self.stt.start_listening()
            self.last_interaction = time.time()

            while self.mode == "DIALOG":
                if time.time() - self.last_interaction > _IDLE_TIMEOUT_SECONDS:
                    self._set_status("MÓWIĘ...")
                    self.tts.speak_wait("Nie słyszę pytania. Do zobaczenia!")
                    break

                self._set_status("SŁUCHAM...")
                text = self.stt.get_text()
                if text:
                    logger.info("recognized: %s", text)
                    self.last_interaction = time.time()
                    self._set_status("MÓWIĘ...")
                    response = self.nlp.get_response(text)
                    self.tts.speak_wait(response)
                    if self._is_goodbye(text):
                        break
                time.sleep(0.1)
        finally:
            self.stt.stop_listening()
            self.mode = "PROMO"
            self.root.after(0, self._reset_ui)


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")


def main() -> None:
    _configure_logging()
    root = tk.Tk()
    VoiceKioskApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
