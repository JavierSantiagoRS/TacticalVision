# TacticalVision

TacticalVision is a local Python computer-vision monitoring system. It uses a webcam or compatible video source to detect and track objects, evaluate configured zones and observable movement patterns, persist events in SQLite, and expose a local FastAPI dashboard.

## Features

- YOLO object detection with ByteTrack object tracking
- Motion, trajectory, behavior, and analytical-priority processing
- ENTER and EXIT zone events, plus analytical alerts and anomalies
- Local SQLite event storage that creates its schema automatically
- FastAPI REST API and a browser dashboard with live refresh
- Zone editor and reusable zone configuration example
- Automated tests

## Architecture

```text
Camera / video source
        |
        v
YOLO + ByteTrack
        |
        v
Object processor (trajectory, motion, behavior)
        |
        v
Zone and event engines -> alert / incident logic
        |
        v
SQLite database -> FastAPI -> web dashboard
```

## Requirements

- Python 3.10 or newer (tested with Python 3.13)
- A webcam or an OpenCV-compatible video source for the processing loop
- Windows is supported by the supplied launcher. Linux and macOS can use the manual commands below.

## Installation

```bash
git clone YOUR_REPOSITORY_URL
cd TacticalVision
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Install test tools when you need to run the test suite:

```bash
pip install -r requirements-dev.txt
```

## Configuration and local data

Project paths are resolved relative to the repository; no personal absolute path is required.

- `src/config.py` contains the camera source, model path, inference image size, confidence threshold, and database path. The default `CAMERA_SOURCE = 0` selects the default webcam.
- `yolo26n.pt` is the 5.5 MB model used by the current pipeline and is kept in the repository because it is comfortably within GitHub's normal file-size limit. The code resolves it from the project root.
- On first API start, `data/tacticalvision.db` and its SQLite schema are created automatically. Runtime database files are intentionally ignored by Git.
- Copy `data/zones.example.json` to `data/zones.json` and adapt the rectangles to configure local zones. The local zone file is ignored because its coordinates are installation-specific.
- This project does not currently require environment variables, so no `.env` file is needed. If one is introduced later, keep it local; `.env` is already ignored.

## Running

On Windows, after installing dependencies, double-click `START_TACTICALVISION.bat`. It starts the API, vision-processing loop, and dashboard, then opens the browser.

To run the components manually from the repository root:

```bash
python -m uvicorn src.api:app --host 127.0.0.1 --port 8000
python -m src.main
python -m http.server 8080 --directory dashboard
```

The API is available at http://127.0.0.1:8000 and the dashboard at http://127.0.0.1:8080. The dashboard routes are `#overview`, `#events`, `#objects`, `#zones`, `#analytics`, and `#system`.

Use `STOP_TACTICALVISION.bat` on Windows to stop processes started by the launcher. It terminates Python processes on the machine, so close unrelated Python work first.

## API

| Endpoint | Description |
| --- | --- |
| `GET /` | API name, version, and availability |
| `GET /api/status` | API availability and persisted event count |
| `GET /api/metrics` | Runtime performance snapshot |
| `GET /api/events?limit=20` | Recent events (limit: 1-100) |
| `GET /api/events/count` | Total persisted events |
| `GET /api/events/types` | Counts grouped by event type |
| `GET /api/events/classes` | Counts grouped by object class |
| `GET /api/events/zones` | Counts grouped by zone |
| `GET /api/anomalies?limit=20` | Recent anomaly events |
| `GET /api/events/zone/{zone_name}` | Events for a zone |
| `GET /api/events/object/{object_id}` | Events for one tracked object |

## Tests

```bash
pytest
```

The current suite is hardware-independent; it does not require a camera or a GUI.

## Project structure

```text
src/                     Application, vision pipeline, API, and persistence
dashboard/               Static HTML, CSS, and JavaScript dashboard
tests/                   Automated tests
data/zones.example.json  Shareable zone configuration template
docs/architecture.md     Component-level architecture notes
launcher.py              Windows launcher implementation
START_TACTICALVISION.bat One-click Windows startup
```

## Troubleshooting

- **API offline:** make sure the API command is running and port 8000 is not in use.
- **Model not found:** confirm that `yolo26n.pt` is present in the project root.
- **Camera unavailable:** update `CAMERA_SOURCE` in `src/config.py` to the correct camera index or compatible source.
- **Port already in use:** stop the process using port 8000 or 8080, or adjust the matching launch command and dashboard API URL together.
- **Missing dependencies:** activate `.venv` and rerun `pip install -r requirements.txt`.

## License

No license has been selected for this repository yet. Choose and add an appropriate license before publishing if you want to grant reuse permissions.
