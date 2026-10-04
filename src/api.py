from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from src.database import Database
from src.metrics import Metrics
from src.dashboard_state import dashboard_state

# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="TacticalVision API",
    version="0.2.0",
    description=(
        "Local computer vision monitoring API "
        "for the TacticalVision project."
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE
# ============================================================

database = Database()
metrics = Metrics()

# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    """
    Return basic API information.
    """

    return {
        "name": "TacticalVision",
        "version": "0.2.0",
        "status": "online",
    }


# ============================================================
# SYSTEM STATUS
# ============================================================

@app.get("/api/status")
def status():
    """
    Return the current system status and event count.
    """

    return {
        "status": "online",
        "events": database.count_events(),
    }

@app.get("/api/metrics")
def system_metrics():
    """
    Return current runtime metrics.
    """

    return dashboard_state.snapshot()

# ============================================================
# EVENTS
# ============================================================

@app.get("/api/events")
def events(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of events to return.",
    )
):
    """
    Return the most recent events.
    """

    rows = database.get_recent_events(
        limit=limit
    )

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# EVENT COUNT
# ============================================================

@app.get("/api/events/count")
def event_count():
    """
    Return the total number of stored events.
    """

    return {
        "total": database.count_events()
    }


# ============================================================
# EVENT TYPES
# ============================================================

@app.get("/api/events/types")
def event_types():
    """
    Return events grouped by event type.
    """

    rows = database.count_events_by_type()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# EVENT CLASSES
# ============================================================

@app.get("/api/events/classes")
def event_classes():
    """
    Return events grouped by detected object class.
    """

    rows = database.count_events_by_class()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# EVENT ZONES
# ============================================================

@app.get("/api/events/zones")
def event_zones():
    """
    Return events grouped by zone.
    """

    rows = database.count_events_by_zone()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# ANOMALIES
# ============================================================

@app.get("/api/anomalies")
def anomalies(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of anomalies to return.",
    )
):
    """
    Return recent anomaly events.
    """

    rows = database.get_anomalies(
        limit=limit
    )

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# EVENTS BY ZONE
# ============================================================

@app.get("/api/events/zone/{zone_name}")
def events_by_zone(
    zone_name: str
):
    """
    Return all events associated with a specific zone.
    """

    rows = database.get_events_by_zone(
        zone_name
    )

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# EVENTS BY OBJECT
# ============================================================

@app.get("/api/events/object/{object_id}")
def events_by_object(
    object_id: int
):
    """
    Return the event history of a tracked object.
    """

    rows = database.get_events_by_object(
        object_id
    )

    return [
        dict(row)
        for row in rows
    ]