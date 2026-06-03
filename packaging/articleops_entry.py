from __future__ import annotations

import threading
import time
import webbrowser
from urllib.error import URLError
from urllib.request import urlopen

from articleops_studio.main import run


APP_URL = "http://127.0.0.1:8000"


def open_browser_when_ready() -> None:
    def wait_and_open() -> None:
        for _ in range(80):
            try:
                with urlopen(APP_URL, timeout=1):
                    webbrowser.open_new(APP_URL)
                    return
            except (OSError, URLError):
                time.sleep(0.25)

        webbrowser.open_new(APP_URL)

    threading.Thread(target=wait_and_open, daemon=True).start()


if __name__ == "__main__":
    open_browser_when_ready()
    run()
