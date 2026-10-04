import subprocess
import time
import webbrowser
from pathlib import Path
import sys
import urllib.request


BASE_DIR = Path(__file__).resolve().parent
PYTHON = BASE_DIR / ".venv" / "Scripts" / "python.exe"


def start_process(command):
    return subprocess.Popen(
        command,
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def wait_for_api(timeout=20):
    url = "http://127.0.0.1:8000/api/status"

    start = time.time()

    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass

        time.sleep(0.5)

    return False


def main():

    print("Starting TacticalVision...")

    if not PYTHON.exists():
        print("ERROR: Python virtual environment not found.")
        input("Press ENTER to exit...")
        sys.exit(1)

    processes = []

    # --------------------------------------------------
    # API
    # --------------------------------------------------

    print("Starting API...")

    api = start_process([
        str(PYTHON),
        "-m",
        "uvicorn",
        "src.api:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
    ])

    processes.append(api)

    print("Waiting for API...")

    if not wait_for_api():
        print("ERROR: API failed to start.")

        for process in processes:
            process.terminate()

        input("Press ENTER to exit...")
        sys.exit(1)

    print("API ONLINE")

    # --------------------------------------------------
    # CORE
    # --------------------------------------------------

    print("Starting TacticalVision Core...")

    core = start_process([
        str(PYTHON),
        "-m",
        "src.main"
    ])

    processes.append(core)

    time.sleep(2)

    # --------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------

    print("Starting Dashboard...")

    dashboard = start_process([
        str(PYTHON),
        "-m",
        "http.server",
        "8080",
        "--directory",
        str(BASE_DIR / "dashboard")
    ])

    processes.append(dashboard)

    time.sleep(2)

    # --------------------------------------------------
    # BROWSER
    # --------------------------------------------------

    print("Opening dashboard...")

    webbrowser.open(
        "http://127.0.0.1:8080"
    )

    print()
    print("==============================")
    print("TACTICALVISION RUNNING")
    print("==============================")
    print()
    print("API:       http://127.0.0.1:8000")
    print("Dashboard: http://127.0.0.1:8080")
    print()


if __name__ == "__main__":
    main()