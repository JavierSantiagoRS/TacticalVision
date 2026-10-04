import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from src.config import DATABASE_PATH


class Database:
    """
    SQLite database manager for TacticalVision.

    Responsible for:
    - Creating the database and schema.
    - Persisting computer-vision events.
    - Querying recent events and statistics.
    - Managing the SQLite connection lifecycle.
    """

    def __init__(self, database_path=DATABASE_PATH):
        self.database_path = Path(database_path)

        # --------------------------------------------------
        # DATABASE DIRECTORY
        # --------------------------------------------------

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # --------------------------------------------------
        # SQLITE CONNECTION
        # --------------------------------------------------

        self.connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        # Improve SQLite reliability.
        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        self.connection.execute(
            "PRAGMA journal_mode = WAL"
        )

        self.connection.execute(
            "PRAGMA busy_timeout = 5000"
        )

        # --------------------------------------------------
        # SCHEMA
        # --------------------------------------------------

        self._create_tables()

    # ======================================================
    # SCHEMA
    # ======================================================

    def _create_tables(self):
        """
        Create the database schema if it does not exist.
        """

        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                object_id INTEGER NOT NULL,

                object_class TEXT NOT NULL,

                event_type TEXT NOT NULL,

                zone TEXT NOT NULL,

                confidence REAL,

                direction TEXT,

                speed REAL,

                reason TEXT,

                timestamp TEXT NOT NULL
            )
            """
        )

        # --------------------------------------------------
        # INDEXES
        # --------------------------------------------------

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_timestamp
            ON events(timestamp)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_object_id
            ON events(object_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_zone
            ON events(zone)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_event_type
            ON events(event_type)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_object_class
            ON events(object_class)
            """
        )

        self.connection.commit()

    # ======================================================
    # SAVE EVENT
    # ======================================================

    def save_event(
        self,
        object_id,
        object_class,
        event_type,
        zone,
        confidence=None,
        direction=None,
        speed=None,
        reason=None
    ):
        """
        Persist a computer-vision event.

        Returns:
            int: ID of the newly created event.
        """

        self._ensure_connection()

        timestamp = datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        )

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO events (
                object_id,
                object_class,
                event_type,
                zone,
                confidence,
                direction,
                speed,
                reason,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                object_id,
                object_class,
                event_type,
                zone,
                confidence,
                direction,
                speed,
                reason,
                timestamp
            )
        )

        self.connection.commit()

        return cursor.lastrowid

    # ======================================================
    # INSERT EVENT
    # ======================================================

    def insert_event(self, event):
        """
        Compatibility wrapper used by TacticalVisionApp.

        Args:
            event:
                Dictionary containing event information.

        Returns:
            int: ID of the inserted event.
        """

        if not isinstance(event, dict):
            raise TypeError(
                "event must be a dictionary"
            )

        required_fields = (
            "object_id",
            "object_class",
            "type",
            "zone"
        )

        missing_fields = [
            field
            for field in required_fields
            if field not in event
        ]

        if missing_fields:
            raise ValueError(
                "Missing event fields: "
                + ", ".join(missing_fields)
            )

        return self.save_event(
            object_id=event["object_id"],
            object_class=event["object_class"],
            event_type=event["type"],
            zone=event["zone"],
            confidence=event.get(
                "confidence"
            ),
            direction=event.get(
                "direction"
            ),
            speed=event.get(
                "speed"
            ),
            reason=event.get(
                "reason"
            )
        )

    # ======================================================
    # RECENT EVENTS
    # ======================================================

    def get_recent_events(self, limit=20):
        """
        Return the most recent events.

        Args:
            limit: Maximum number of events.

        Returns:
            list[sqlite3.Row]
        """

        self._validate_limit(limit)

        self._ensure_connection()

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                object_id,
                object_class,
                event_type,
                zone,
                confidence,
                direction,
                speed,
                reason,
                timestamp
            FROM events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )

        return cursor.fetchall()

    # ======================================================
    # EVENTS BY ZONE
    # ======================================================

    def get_events_by_zone(self, zone):
        """
        Return all events associated with a zone.
        """

        self._ensure_connection()

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                object_id,
                object_class,
                event_type,
                zone,
                confidence,
                direction,
                speed,
                reason,
                timestamp
            FROM events
            WHERE zone = ?
            ORDER BY id DESC
            """,
            (zone,)
        )

        return cursor.fetchall()

    # ======================================================
    # EVENTS BY OBJECT
    # ======================================================

    def get_events_by_object(self, object_id):
        """
        Return the event history of a tracked object.
        """

        self._ensure_connection()

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                object_id,
                object_class,
                event_type,
                zone,
                confidence,
                direction,
                speed,
                reason,
                timestamp
            FROM events
            WHERE object_id = ?
            ORDER BY id DESC
            """,
            (object_id,)
        )

        return cursor.fetchall()

    # ======================================================
    # EVENT COUNT
    # ======================================================

    def count_events(self):
        """
        Return the total number of stored events.
        """

        self._ensure_connection()

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM events
            """
        )

        row = cursor.fetchone()

        return int(row["total"])

    # ======================================================
    # EVENTS BY TYPE
    # ======================================================

    def count_events_by_type(self):
        """
        Return event counts grouped by event type.
        """

        self._ensure_connection()

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                event_type,
                COUNT(*) AS total
            FROM events
            GROUP BY event_type
            ORDER BY total DESC
            """
        )

        return cursor.fetchall()

    # ======================================================
    # EVENTS BY CLASS
    # ======================================================

    def count_events_by_class(self):
        """
        Return event counts grouped by detected class.
        """

        self._ensure_connection()

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                object_class,
                COUNT(*) AS total
            FROM events
            GROUP BY object_class
            ORDER BY total DESC
            """
        )

        return cursor.fetchall()

    # ======================================================
    # EVENTS BY ZONE
    # ======================================================

    def count_events_by_zone(self):
        """
        Return event counts grouped by zone.
        """

        self._ensure_connection()

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                zone,
                COUNT(*) AS total
            FROM events
            GROUP BY zone
            ORDER BY total DESC
            """
        )

        return cursor.fetchall()

    # ======================================================
    # ANOMALIES
    # ======================================================

    def get_anomalies(self, limit=20):
        """
        Return the most recent anomaly events.
        """

        self._validate_limit(limit)

        self._ensure_connection()

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                object_id,
                object_class,
                event_type,
                zone,
                confidence,
                direction,
                speed,
                reason,
                timestamp
            FROM events
            WHERE event_type = 'ANOMALY'
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )

        return cursor.fetchall()

    # ======================================================
    # CLEAR EVENTS
    # ======================================================

    def clear_events(self):
        """
        Delete all stored events.

        Intended mainly for development/testing.
        """

        self._ensure_connection()

        cursor = self.connection.cursor()

        cursor.execute(
            """
            DELETE FROM events
            """
        )

        self.connection.commit()

    # ======================================================
    # HEALTH CHECK
    # ======================================================

    def health_check(self):
        """
        Verify that the SQLite connection is operational.

        Returns:
            bool
        """

        if self.connection is None:
            return False

        try:

            cursor = self.connection.cursor()

            cursor.execute(
                "SELECT 1"
            )

            result = cursor.fetchone()

            return result is not None

        except sqlite3.Error:

            return False

    # ======================================================
    # CONNECTION VALIDATION
    # ======================================================

    def _ensure_connection(self):
        """
        Ensure the database connection is available.
        """

        if self.connection is None:
            raise RuntimeError(
                "Database connection is closed."
            )

    # ======================================================
    # LIMIT VALIDATION
    # ======================================================

    @staticmethod
    def _validate_limit(limit):
        """
        Validate query limits.
        """

        if not isinstance(
            limit,
            int
        ):
            raise TypeError(
                "limit must be an integer"
            )

        if limit < 1:
            raise ValueError(
                "limit must be >= 1"
            )

    # ======================================================
    # CLOSE
    # ======================================================

    def close(self):
        """
        Close the SQLite connection safely.
        """

        if self.connection is None:
            return

        try:

            self.connection.close()

        finally:

            self.connection = None