"""Optional companion display: fullscreen Chromium showing the static menu page.

The voice assistant itself runs as the Tkinter app in :mod:`src.main`. This
module is only for venues with a second screen that shows ``index.html`` (the
static menu) locked into kiosk mode — it is independent of the voice loop.
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_CHROMIUM_FLAGS = (
    "--kiosk",
    "--incognito",
    "--no-first-run",
    "--disable-pinch",
    "--overscroll-history-navigation=0",
    "--disable-features=TranslateUI",
    "--disk-cache-dir=/dev/null",
    "--disable-session-crashed-bubble",
    "--disable-infobars",
    "--check-for-update-interval=31536000",
)


class KioskDisplay:
    """Manage a full-screen Chromium instance pointed at the local menu page."""

    def __init__(self) -> None:
        self.process: subprocess.Popen[bytes] | None = None
        self._env = {
            "DISPLAY": os.environ.get("DISPLAY", ":0"),
            "XAUTHORITY": os.environ.get("XAUTHORITY", os.path.expanduser("~/.Xauthority")),
        }

    def start(self, page: Path = Path("index.html")) -> bool:
        """Launch Chromium fullscreen pointed at the local menu page."""
        if not self._x_server_available():
            logger.warning("no X server found; skipping fullscreen display")
            return False

        self._kill_existing()
        url = page.resolve().as_uri()
        logger.info("starting kiosk display: %s", url)
        self.process = subprocess.Popen(
            ["chromium-browser", *_CHROMIUM_FLAGS, url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=self._env,
        )
        return True

    def stop(self) -> None:
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self._kill_existing()
        logger.info("kiosk display stopped")

    def _x_server_available(self) -> bool:
        try:
            result = subprocess.run(
                ["xset", "-q"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=self._env,
                check=False,
            )
        except FileNotFoundError:
            return False
        return result.returncode == 0

    @staticmethod
    def _kill_existing() -> None:
        subprocess.run(["pkill", "-f", "chromium.*kiosk"], stderr=subprocess.DEVNULL, check=False)
        time.sleep(1)
