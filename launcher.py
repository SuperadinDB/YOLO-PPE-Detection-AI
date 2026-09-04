import os
import sys
import time
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path


def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:8501")


if __name__ == "__main__":
    app_path = resource_path("app.py")

    import threading

    threading.Thread(
        target=open_browser,
        daemon=True,
    ).start()

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--global.developmentMode=false",
        "--server.headless=true",
        "--server.port=8501",
        "--browser.gatherUsageStats=false",
    ]

    sys.exit(stcli.main())