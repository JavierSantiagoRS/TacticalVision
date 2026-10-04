from pathlib import Path


# ==========================================================
# PROJECT PATHS
# ==========================================================

# Root directory of the TacticalVision project.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================================
# DATA
# ==========================================================

DATA_DIR = BASE_DIR / "data"

DATABASE_PATH = DATA_DIR / "tacticalvision.db"
ZONES_PATH = DATA_DIR / "zones.json"


# ==========================================================
# CAMERA
# ==========================================================

# OpenCV camera source.
#
# 0 = default webcam
# 1 = secondary webcam
#
# A video file path can also be used if required.
CAMERA_SOURCE = 0


# ==========================================================
# YOLO / COMPUTER VISION
# ==========================================================

# YOLO model used by the detection pipeline.
MODEL_PATH = BASE_DIR / "yolo26n.pt"

# Input resolution used during inference.
#
# Lower values improve performance on systems
# with limited RAM/CPU/GPU resources.
IMAGE_SIZE = 320

# Minimum detection confidence.
CONFIDENCE_THRESHOLD = 0.35


# ==========================================================
# OBJECT TRACKING
# ==========================================================

# Ultralytics tracker configuration.
TRACKER_CONFIG = "bytetrack.yaml"


# ==========================================================
# ANOMALY ANALYSIS
# ==========================================================

# Score at which an object enters the SUSPICIOUS state.
ANOMALY_SUSPICIOUS_THRESHOLD = 40

# Score at which an object enters the ALERT state.
ANOMALY_ALERT_THRESHOLD = 70


# ==========================================================
# ZONE CONFIGURATION
# ==========================================================

# Zone type used when a zone does not explicitly define one.
#
# Available conceptual zone types:
#
# MONITORING
# RESTRICTED
# HIGH_SENSITIVITY
#
DEFAULT_ZONE_TYPE = "MONITORING"


# ==========================================================
# APPLICATION
# ==========================================================

WINDOW_NAME = "TacticalVision"


# ==========================================================
# SYSTEM INFORMATION
# ==========================================================

APP_NAME = "TacticalVision"
APP_VERSION = "0.2.0"

SYSTEM_DESCRIPTION = (
    "AI-assisted situational awareness "
    "and computer vision monitoring platform"
)
