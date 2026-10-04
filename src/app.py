import time

import cv2

from src.alert_engine import AlertEngine
from src.dashboard_state import dashboard_state
from src.alert_policy import AlertPolicy
from src.behavior import BehaviorAnalyzer
from src.camera import Camera
from src.class_stabilizer import ClassStabilizer
from src.config import WINDOW_NAME
from src.database import Database
from src.event_engine import EventEngine
from src.incident_manager import IncidentManager
from src.metrics import Metrics
from src.motion import MotionAnalyzer
from src.object_processor import ObjectProcessor
from src.tactical_state import TacticalState
from src.threat import ThreatAssessment
from src.tracker import ObjectTracker
from src.trajectory import TrajectoryTracker
from src.zone_storage import ZoneStorage


class TacticalVisionApp:
    """
    Main TacticalVision application.

    Educational computer-vision analytics pipeline:

        Camera
          |
          v
        YOLO
          |
          v
        ByteTrack
          |
          v
        Class Stabilizer
          |
          v
        ObjectProcessor
          +-- Trajectory Analysis
          +-- Motion Analysis
          +-- Behavior Analysis
          |
          v
        Zone Analysis
          |
          v
        Analytical Priority Assessment
          |
          v
        Alert Policy
          |
          v
        Alert Engine
          |
          v
        Incident Manager
          |
          v
        TacticalState
          |
          v
        SQLite

    The system evaluates observable computer-vision signals.

    It does not:
        - identify people,
        - infer identity,
        - infer intent,
        - determine real-world threats,
        - perform targeting.
    """

    def __init__(self):

        # ==================================================
        # APPLICATION LIFECYCLE
        # ==================================================

        self._running = False
        self._stopped = False

        # ==================================================
        # CORE COMPONENTS
        # ==================================================

        self.camera = Camera()

        self.tracker = ObjectTracker()

        self.trajectory_tracker = (
            TrajectoryTracker()
        )

        self.motion_analyzer = (
            MotionAnalyzer()
        )

        self.behavior_analyzer = (
            BehaviorAnalyzer()
        )

        # ==================================================
        # CLASS STABILIZATION
        # ==================================================
        #
        # YOLO can occasionally change the predicted class
        # of the same tracked object between frames.
        #
        # Example:
        #
        #     person
        #     person
        #     remote
        #     person
        #
        # ClassStabilizer keeps a short temporal history
        # for every tracking ID and returns the dominant class.
        #

        self.class_stabilizer = (
            ClassStabilizer(
                history_size=8,
                minimum_observations=3
            )
        )

        # ==================================================
        # OBJECT PROCESSOR
        # ==================================================
        #
        # Centralizes:
        #   - trajectory
        #   - motion
        #   - behavior
        #

        self.object_processor = (
            ObjectProcessor(
                trajectory_tracker=self.trajectory_tracker,
                motion_analyzer=self.motion_analyzer,
                behavior_analyzer=self.behavior_analyzer,
            )
        )

        # ==================================================
        # ANALYTICAL PIPELINE
        # ==================================================

        self.event_engine = (
            EventEngine()
        )

        self.threat_assessment = (
            ThreatAssessment()
        )

        self.alert_policy = (
            AlertPolicy()
        )

        self.alert_engine = (
            AlertEngine()
        )

        self.incident_manager = (
            IncidentManager()
        )

        # ==================================================
        # STORAGE
        # ==================================================

        self.zone_storage = (
            ZoneStorage()
        )

        self.database = (
            Database()
        )

        # ==================================================
        # METRICS
        # ==================================================

        self.metrics = (
            Metrics()
        )

        # ==================================================
        # CENTRALIZED APPLICATION STATE
        # ==================================================

        self.tactical_state = (
            TacticalState()
        )

        # ==================================================
        # ANALYTICAL STATE
        # ==================================================

        # Maps:
        #
        #     (object_id, zone) -> previous behavior status
        #

        self.anomaly_states = {}

        # Maps:
        #
        #     (object_id, zone) -> current analytical alert state
        #

        self.alert_states = {}

        # Maps:
        #
        #     (object_id, zone) -> incident_id
        #

        self.incident_states = {}

        # ==================================================
        # LOAD CONFIGURED ZONES
        # ==================================================

        self.zones = (
            self.zone_storage.load()
        )

        print(
            "[SYSTEM] "
            f"Loaded {len(self.zones)} zone(s)."
        )

    # ======================================================
    # MAIN LOOP
    # ======================================================

    def start(self):
        """
        Start the TacticalVision processing loop.
        """

        if self._running:

            print(
                "[SYSTEM] "
                "Application is already running."
            )

            return

        if self._stopped:

            print(
                "[SYSTEM] "
                "Application has already been stopped."
            )

            return

        print()
        print("======================================")
        print("          TACTICALVISION")
        print("======================================")
        print()
        print("[SYSTEM] Starting application...")
        print("[SYSTEM] Press Q to exit.")
        print()

        self._running = True

        try:

            # ==================================================
            # CAMERA INITIALIZATION
            # ==================================================

            print(
                "[SYSTEM] Opening camera..."
            )

            self.camera.open()

            self.tactical_state.set_system_status(
                "OPERATIONAL"
            )

            dashboard_state.set_status("OPERATIONAL")

            print(
                "[SYSTEM] Camera ready."
            )

            print()

            # ==================================================
            # MAIN PROCESSING LOOP
            # ==================================================

            while self._running:

                self.metrics.start_frame()

                # ----------------------------------------------
                # CAPTURE FRAME
                # ----------------------------------------------

                frame = self.camera.read()

                if frame is None:

                    print(
                        "[ERROR] "
                        "Camera returned an empty frame."
                    )

                    self.tactical_state.set_system_status(
                        "ERROR"
                    )

                    break

                dashboard_state.set_status("OPERATIONAL")

                # ----------------------------------------------
                # OBJECT TRACKING
                # ----------------------------------------------

                inference_start = (
                    time.perf_counter()
                )

                result = (
                    self.tracker.track(
                        frame
                    )
                )

                inference_time = (
                    time.perf_counter()
                    - inference_start
                )

                self.metrics.record_inference(
                    inference_time
                )

                # ----------------------------------------------
                # PROCESS TRACKED OBJECTS
                # ----------------------------------------------

                active_ids = (
                    self._process_tracks(
                        frame,
                        result
                    )
                )

                # ----------------------------------------------
                # CLEAN STALE OBJECT PROCESSOR STATE
                # ----------------------------------------------

                self.object_processor.remove_stale(
                    active_ids
                )

                # ----------------------------------------------
                # CLEAN STALE CLASS HISTORIES
                # ----------------------------------------------

                self.class_stabilizer.remove(
                    active_ids
                )

                # ----------------------------------------------
                # CLEAN STALE ANOMALY STATE
                # ----------------------------------------------

                self._remove_stale_anomaly_states(
                    active_ids
                )

                # ----------------------------------------------
                # CLEAN STALE ALERT ENGINE STATE
                # ----------------------------------------------

                self.alert_engine.remove(
                    active_ids
                )

                # ----------------------------------------------
                # CLEAN STALE ALERT STATE
                # ----------------------------------------------

                self._remove_stale_alert_states(
                    active_ids
                )

                # ----------------------------------------------
                # CLEAN STALE INCIDENT REFERENCES
                # ----------------------------------------------

                self._remove_stale_incident_states(
                    active_ids
                )

                # ----------------------------------------------
                # CLEAN STALE CENTRALIZED TRACK STATE
                # ----------------------------------------------

                self.tactical_state.remove_tracks(
                    active_ids
                )

                # ----------------------------------------------
                # ACTIVE OBJECT METRIC
                # ----------------------------------------------

                self.metrics.set_active_objects(
                    len(active_ids)
                )

                # ----------------------------------------------
                # DRAW ZONES
                # ----------------------------------------------

                self._draw_zones(
                    frame
                )

                # ----------------------------------------------
                # DRAW METRICS
                # ----------------------------------------------

                self._draw_metrics(
                    frame
                )

                # ----------------------------------------------
                # FINISH FRAME METRICS
                # ----------------------------------------------

                self.metrics.end_frame()

                dashboard_state.update_metrics(
    self.metrics.snapshot()
)

                # ----------------------------------------------
                # DISPLAY
                # ----------------------------------------------

                cv2.imshow(
                    WINDOW_NAME,
                    frame
                )

                # ----------------------------------------------
                # KEYBOARD INPUT
                # ----------------------------------------------

                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )

                if key == ord("q"):

                    print(
                        "[SYSTEM] "
                        "Exit requested by user."
                    )

                    break

        except KeyboardInterrupt:

            print()

            print(
                "[SYSTEM] "
                "Interrupted by user."
            )

            self.tactical_state.set_system_status(
                "STOPPING"
            )

        except Exception as error:

            dashboard_state.set_status("STOPPING")

            self.tactical_state.set_system_status(
                "ERROR"
            )

            dashboard_state.set_status("ERROR")

            print()

            print(
                "[FATAL] "
                f"{type(error).__name__}: "
                f"{error}"
            )

            raise

        finally:

            self._running = False

            self.stop()

    # ======================================================
    # PROCESS TRACKS
    # ======================================================

    def _process_tracks(
        self,
        frame,
        result
    ):
        """
        Process all currently tracked objects.

        Returns:
            set[int]:
                IDs currently visible and tracked.
        """

        active_ids = set()

        # ----------------------------------------------
        # VALIDATE TRACKING RESULT
        # ----------------------------------------------

        if result is None:

            return active_ids

        boxes = getattr(
            result,
            "boxes",
            None
        )

        if boxes is None:

            return active_ids

        # ----------------------------------------------
        # TRACK IDS
        # ----------------------------------------------

        ids_tensor = getattr(
            boxes,
            "id",
            None
        )

        if ids_tensor is None:

            return active_ids

        try:

            ids = (
                ids_tensor
                .int()
                .cpu()
                .tolist()
            )

        except Exception:

            return active_ids

        # ----------------------------------------------
        # BOUNDING BOXES
        # ----------------------------------------------

        xyxy_tensor = getattr(
            boxes,
            "xyxy",
            None
        )

        if xyxy_tensor is None:

            return active_ids

        try:

            xyxy = (
                xyxy_tensor
                .cpu()
                .tolist()
            )

        except Exception:

            return active_ids

        # ----------------------------------------------
        # CLASS IDS
        # ----------------------------------------------

        classes_tensor = getattr(
            boxes,
            "cls",
            None
        )

        if classes_tensor is None:

            return active_ids

        try:

            classes = (
                classes_tensor
                .int()
                .cpu()
                .tolist()
            )

        except Exception:

            return active_ids

        # ----------------------------------------------
        # CONFIDENCES
        # ----------------------------------------------

        confidences_tensor = getattr(
            boxes,
            "conf",
            None
        )

        if confidences_tensor is None:

            confidences = [
                0.0
                for _ in ids
            ]

        else:

            try:

                confidences = (
                    confidences_tensor
                    .cpu()
                    .tolist()
                )

            except Exception:

                confidences = [
                    0.0
                    for _ in ids
                ]

        # ----------------------------------------------
        # PROCESS OBJECTS
        # ----------------------------------------------

        object_count = min(
            len(ids),
            len(xyxy),
            len(classes),
            len(confidences)
        )

        for index in range(
            object_count
        ):

            object_id = int(
                ids[index]
            )

            bbox = xyxy[index]

            class_id = int(
                classes[index]
            )

            confidence = self._safe_float(
                confidences[index],
                default=0.0
            )

            active_ids.add(
                object_id
            )

            # ------------------------------------------
            # BOUNDING BOX
            # ------------------------------------------

            if (
                not isinstance(
                    bbox,
                    (list, tuple)
                )
                or len(bbox) < 4
            ):

                continue

            try:

                x1, y1, x2, y2 = map(
                    int,
                    bbox[:4]
                )

            except (
                TypeError,
                ValueError
            ):

                continue

            # ------------------------------------------
            # CENTER POINT
            # ------------------------------------------

            center_x = int(
                (x1 + x2) / 2
            )

            center_y = int(
                (y1 + y2) / 2
            )

            # ------------------------------------------
            # RAW OBJECT CLASS
            # ------------------------------------------

            raw_object_class = (
                self._get_class_name(
                    result,
                    class_id
                )
            )

            # ------------------------------------------
            # CLASS STABILIZATION
            # ------------------------------------------
            #
            # Important:
            #
            # The detector's raw prediction is not
            # immediately used by the analytical pipeline.
            #
            # Instead, the ClassStabilizer maintains a
            # temporal history for this tracking ID.
            #

            object_class = (
                self.class_stabilizer.update(
                    object_id=object_id,
                    object_class=raw_object_class
                )
            )

            # ------------------------------------------
            # OBJECT PROCESSOR
            # ------------------------------------------
            #
            # Trajectory
            # Motion
            # Behavior
            #

            processed = (
                self.object_processor.process(
                    object_id=object_id,
                    x=center_x,
                    y=center_y
                )
            )

            if not isinstance(
                processed,
                dict
            ):

                processed = {}

            motion = processed.get(
                "motion"
            )

            behavior = processed.get(
                "behavior"
            )

            # ------------------------------------------
            # CURRENT ZONE
            # ------------------------------------------

            current_zone = (
                self._get_current_zone(
                    center_x,
                    center_y
                )
            )

            # ------------------------------------------
            # BEHAVIOR STATUS
            # ------------------------------------------

            behavior_status = (
                self._get_behavior_status(
                    behavior
                )
            )

            # ------------------------------------------
            # SPEED
            # ------------------------------------------

            speed = (
                self._get_speed(
                    motion
                )
            )

            # ------------------------------------------
            # THREAT / RISK ASSESSMENT
            # ------------------------------------------

            assessment = (
                self.threat_assessment.assess(
                    object_class=object_class,
                    zone_name=current_zone,
                    speed=speed,
                    behavior_status=behavior_status
                )
            )

            if not isinstance(
                assessment,
                dict
            ):

                assessment = {
                    "priority": "NORMAL",
                    "score": 0,
                    "reasons": []
                }

            priority = (
                assessment.get(
                    "priority",
                    "NORMAL"
                )
            )

            score = (
                self._safe_float(
                    assessment.get(
                        "score",
                        0
                    ),
                    default=0.0
                )
            )

            reasons = assessment.get(
                "reasons",
                []
            )

            if not isinstance(
                reasons,
                list
            ):

                reasons = (
                    list(reasons)
                    if reasons
                    else []
                )

            # ------------------------------------------
            # ALERT POLICY
            # ------------------------------------------

            alert_status = (
                self.alert_policy.evaluate(
                    priority
                )
            )

            # ------------------------------------------
            # ALERT ENGINE
            # ------------------------------------------

            alert = (
                self.alert_engine.update(
                    object_id=object_id,
                    zone=current_zone,
                    status=alert_status,
                    score=score,
                    reasons=reasons
                )
            )

            # ------------------------------------------
            # CURRENT ANALYTICAL STATE
            # ------------------------------------------

            alert_key = (
                object_id,
                current_zone
            )

            self.alert_states[
                alert_key
            ] = {
                "priority": priority,
                "score": score,
                "status": alert_status,
                "reasons": list(
                    reasons
                )
            }

            # ------------------------------------------
            # CENTRALIZED TACTICAL STATE
            # ------------------------------------------

            direction = (
                self._get_direction(
                    motion
                )
            )

            self.tactical_state.update_track(
                object_id=object_id,
                object_class=object_class,
                zone=current_zone,
                speed=speed,
                direction=direction,
                behavior=behavior_status,
                priority=priority
            )

            # ------------------------------------------
            # NEW ALERT
            # ------------------------------------------

            if alert is not None:

                self._process_alert(
                    alert=alert,
                    object_id=object_id,
                    object_class=object_class,
                    zone_name=current_zone,
                    confidence=confidence,
                    motion=motion,
                    assessment=assessment
                )

            # ------------------------------------------
            # DRAW OBJECT
            # ------------------------------------------

            self._draw_object(
                frame=frame,
                object_id=object_id,
                object_class=object_class,
                confidence=confidence,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                center_x=center_x,
                center_y=center_y,
                motion=motion,
                behavior=behavior,
                assessment=assessment,
                alert_status=alert_status
            )

            # ------------------------------------------
            # DRAW TRAJECTORY
            # ------------------------------------------

            self._draw_trajectory(
                frame,
                object_id
            )

            # ------------------------------------------
            # BEHAVIOR EVENTS
            # ------------------------------------------

            self._process_behavior(
                object_id=object_id,
                object_class=object_class,
                zone_name=current_zone,
                confidence=confidence,
                motion=motion,
                behavior=behavior
            )

            # ------------------------------------------
            # ZONE EVENTS
            # ------------------------------------------

            self._process_zones(
                object_id=object_id,
                object_class=object_class,
                x=center_x,
                y=center_y,
                confidence=confidence,
                motion=motion
            )

        return active_ids

    # ======================================================
    # CLASS NAME
    # ======================================================

    def _get_class_name(
        self,
        result,
        class_id
    ):
        """
        Resolve the model class ID into a class name.
        """

        names = getattr(
            result,
            "names",
            None
        )

        if names is None:

            return str(class_id)

        try:

            class_id = int(
                class_id
            )

        except (
            TypeError,
            ValueError
        ):

            return str(class_id)

        if isinstance(
            names,
            dict
        ):

            return str(
                names.get(
                    class_id,
                    class_id
                )
            )

        try:

            if (
                0 <= class_id
                < len(names)
            ):

                return str(
                    names[class_id]
                )

        except (
            TypeError,
            IndexError
        ):

            pass

        return str(class_id)

    # ======================================================
    # CURRENT ZONE
    # ======================================================

    def _get_current_zone(
        self,
        x,
        y
    ):
        """
        Return the first configured zone containing
        the object's center point.
        """

        for zone in self.zones:

            try:

                if zone.contains(
                    x,
                    y
                ):

                    return zone.name

            except Exception:

                continue

        return "NO_ZONE"

    # ======================================================
    # BEHAVIOR STATUS
    # ======================================================

    @staticmethod
    def _get_behavior_status(
        behavior
    ):
        """
        Extract and normalize behavior status.
        """

        if not isinstance(
            behavior,
            dict
        ):

            return "NORMAL"

        status = behavior.get(
            "status",
            "NORMAL"
        )

        if not isinstance(
            status,
            str
        ):

            return "NORMAL"

        return status.upper()

    # ======================================================
    # SPEED
    # ======================================================

    @staticmethod
    def _get_speed(
        motion
    ):
        """
        Extract a safe non-negative speed value.
        """

        if not isinstance(
            motion,
            dict
        ):

            return 0.0

        return max(
            0.0,
            TacticalVisionApp._safe_float(
                motion.get(
                    "speed",
                    0.0
                ),
                default=0.0
            )
        )

    # ======================================================
    # DIRECTION
    # ======================================================

    @staticmethod
    def _get_direction(
        motion
    ):
        """
        Extract a normalized direction value.
        """

        if not isinstance(
            motion,
            dict
        ):

            return "UNKNOWN"

        direction = motion.get(
            "direction",
            "UNKNOWN"
        )

        if not isinstance(
            direction,
            str
        ):

            return "UNKNOWN"

        return direction.upper()

    # ======================================================
    # DRAW OBJECT
    # ======================================================

    def _draw_object(
        self,
        frame,
        object_id,
        object_class,
        confidence,
        x1,
        y1,
        x2,
        y2,
        center_x,
        center_y,
        motion,
        behavior,
        assessment,
        alert_status
    ):
        """
        Draw tracked-object analytical information.
        """

        # ----------------------------------------------
        # BOUNDING BOX
        # ----------------------------------------------

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (255, 255, 255),
            2
        )

        # ----------------------------------------------
        # CENTER POINT
        # ----------------------------------------------

        cv2.circle(
            frame,
            (center_x, center_y),
            4,
            (255, 255, 255),
            -1
        )

        # ----------------------------------------------
        # OBJECT LABEL
        # ----------------------------------------------

        label = (
            f"ID {object_id} | "
            f"{object_class} | "
            f"{confidence:.2f}"
        )

        cv2.putText(
            frame,
            label,
            (
                x1,
                max(
                    y1 - 10,
                    20
                )
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2
        )

        # ----------------------------------------------
        # MOTION
        # ----------------------------------------------

        if isinstance(
            motion,
            dict
        ):

            direction = self._get_direction(
                motion
            )

            speed = self._get_speed(
                motion
            )

            motion_text = (
                f"{direction} "
                f"{speed:.1f}px/s"
            )

            cv2.putText(
                frame,
                motion_text,
                (
                    x1,
                    y2 + 20
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                1
            )

        # ----------------------------------------------
        # BEHAVIOR
        # ----------------------------------------------

        if isinstance(
            behavior,
            dict
        ):

            behavior_status = (
                self._get_behavior_status(
                    behavior
                )
            )

            behavior_reason = behavior.get(
                "reason"
            )

            if behavior_status == "ANOMALY":

                behavior_text = "ANOMALY"

                if behavior_reason:

                    behavior_text = (
                        f"ANOMALY: "
                        f"{behavior_reason}"
                    )

                cv2.putText(
                    frame,
                    behavior_text,
                    (
                        x1,
                        y2 + 40
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (255, 255, 255),
                    2
                )

        # ----------------------------------------------
        # ANALYTICAL PRIORITY
        # ----------------------------------------------

        if isinstance(
            assessment,
            dict
        ):

            priority = assessment.get(
                "priority",
                "NORMAL"
            )

            score = self._safe_float(
                assessment.get(
                    "score",
                    0
                ),
                default=0.0
            )

            priority_text = (
                f"PRIORITY: "
                f"{priority} "
                f"[{score:.0f}]"
            )

            cv2.putText(
                frame,
                priority_text,
                (
                    x1,
                    y2 + 60
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                1
            )

        # ----------------------------------------------
        # ALERT STATUS
        # ----------------------------------------------

        if alert_status != "NORMAL":

            alert_text = (
                f"STATUS: "
                f"{alert_status}"
            )

            cv2.putText(
                frame,
                alert_text,
                (
                    x1,
                    y2 + 80
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                2
            )

    # ======================================================
    # DRAW TRAJECTORY
    # ======================================================

    def _draw_trajectory(
        self,
        frame,
        object_id
    ):
        """
        Draw the historical trajectory for a tracked object.
        """

        trajectory = (
            self.object_processor.get_trajectory(
                object_id
            )
        )

        if not trajectory:

            return

        if len(trajectory) < 2:

            return

        for index in range(
            1,
            len(trajectory)
        ):

            previous_point = (
                trajectory[
                    index - 1
                ]
            )

            current_point = (
                trajectory[
                    index
                ]
            )

            try:

                cv2.line(
                    frame,
                    tuple(previous_point),
                    tuple(current_point),
                    (255, 255, 255),
                    2
                )

            except (
                TypeError,
                ValueError
            ):

                continue

    # ======================================================
    # PROCESS ZONES
    # ======================================================

    def _process_zones(
        self,
        object_id,
        object_class,
        x,
        y,
        confidence=None,
        motion=None
    ):
        """
        Feed the current object position to the zone
        event engine.
        """

        direction = None
        speed = None

        if isinstance(
            motion,
            dict
        ):

            direction = motion.get(
                "direction"
            )

            speed = motion.get(
                "speed"
            )

        for zone in self.zones:

            event = (
                self.event_engine.update(
                    object_id=object_id,
                    object_class=object_class,
                    x=x,
                    y=y,
                    zone=zone,
                    confidence=confidence,
                    direction=direction,
                    speed=speed
                )
            )

            if event is None:

                continue

            # ------------------------------------------
            # EVENT METRIC
            # ------------------------------------------

            self.metrics.record_event()

            # ------------------------------------------
            # CENTRALIZED EVENT STATE
            # ------------------------------------------

            self.tactical_state.add_event(
                event
            )

            # ------------------------------------------
            # CONSOLE
            # ------------------------------------------

            print(
                "[EVENT] "
                f"{event.get('type', 'UNKNOWN')} | "
                f"ID={event.get('object_id', object_id)} | "
                f"CLASS={event.get('object_class', object_class)} | "
                f"ZONE={event.get('zone', zone.name)}"
            )

            # ------------------------------------------
            # DATABASE
            # ------------------------------------------

            self._save_event(
                event
            )

    # ======================================================
    # PROCESS BEHAVIOR
    # ======================================================

    def _process_behavior(
        self,
        object_id,
        object_class,
        zone_name,
        confidence,
        motion,
        behavior
    ):
        """
        Convert a behavior-state transition into an event.

        Only the transition into ANOMALY creates an event.
        """

        if not isinstance(
            behavior,
            dict
        ):

            return

        status = self._get_behavior_status(
            behavior
        )

        reason = behavior.get(
            "reason"
        )

        key = (
            object_id,
            zone_name
        )

        previous_status = (
            self.anomaly_states.get(
                key,
                "NORMAL"
            )
        )

        # ------------------------------------------
        # ANOMALY START
        # ------------------------------------------

        if (
            status == "ANOMALY"
            and previous_status != "ANOMALY"
        ):

            direction = None
            speed = None

            if isinstance(
                motion,
                dict
            ):

                direction = motion.get(
                    "direction"
                )

                speed = motion.get(
                    "speed"
                )

            event = {
                "type": "ANOMALY",
                "object_id": object_id,
                "object_class": object_class,
                "zone": zone_name,
                "confidence": confidence,
                "direction": direction,
                "speed": speed,
                "reason": reason
            }

            # ------------------------------------------
            # METRIC
            # ------------------------------------------

            self.metrics.record_event()

            # ------------------------------------------
            # CENTRALIZED STATE
            # ------------------------------------------

            self.tactical_state.add_event(
                event
            )

            # ------------------------------------------
            # CONSOLE
            # ------------------------------------------

            print(
                "[ANOMALY] "
                f"ID={object_id} | "
                f"CLASS={object_class} | "
                f"ZONE={zone_name} | "
                f"REASON={reason}"
            )

            # ------------------------------------------
            # DATABASE
            # ------------------------------------------

            self._save_event(
                event
            )

        # ------------------------------------------
        # UPDATE BEHAVIOR STATE
        # ------------------------------------------

        self.anomaly_states[
            key
        ] = status

    # ======================================================
    # PROCESS ALERT
    # ======================================================

    def _process_alert(
        self,
        alert,
        object_id,
        object_class,
        zone_name,
        confidence,
        motion,
        assessment
    ):
        """
        Process a newly generated alert transition.
        """

        if alert is None:

            return

        speed = None
        direction = None

        if isinstance(
            motion,
            dict
        ):

            speed = motion.get(
                "speed"
            )

            direction = motion.get(
                "direction"
            )

        reasons = []

        if isinstance(
            assessment,
            dict
        ):

            raw_reasons = assessment.get(
                "reasons",
                []
            )

            if isinstance(
                raw_reasons,
                list
            ):

                reasons = list(
                    raw_reasons
                )

        alert_reasons = alert.get(
            "reasons",
            reasons
        )

        if not isinstance(
            alert_reasons,
            list
        ):

            alert_reasons = reasons

        reason_text = ", ".join(
            str(reason)
            for reason in alert_reasons
        )

        # ------------------------------------------
        # DATABASE EVENT
        # ------------------------------------------

        event = {
            "type": "ALERT",
            "object_id": object_id,
            "object_class": object_class,
            "zone": zone_name,
            "confidence": confidence,
            "direction": direction,
            "speed": speed,
            "reason": reason_text
        }

        # ------------------------------------------
        # EVENT METRIC
        # ------------------------------------------

        self.metrics.record_event()

        # ------------------------------------------
        # CENTRALIZED ALERT STATE
        # ------------------------------------------

        tactical_alert = {
            "type": "ALERT",
            "object_id": object_id,
            "object_class": object_class,
            "zone": zone_name,
            "status": alert.get(
                "status",
                "NORMAL"
            ),
            "score": alert.get(
                "score",
                0
            ),
            "reasons": list(
                alert_reasons
            )
        }

        self.tactical_state.add_alert(
            tactical_alert
        )

        # ------------------------------------------
        # CONSOLE
        # ------------------------------------------

        print(
            "[ALERT] "
            f"ID={object_id} | "
            f"CLASS={object_class} | "
            f"ZONE={zone_name} | "
            f"STATUS={alert.get('status', 'NORMAL')} | "
            f"SCORE={alert.get('score', 0)} | "
            f"REASONS={reason_text}"
        )

        # ------------------------------------------
        # DATABASE
        # ------------------------------------------

        self._save_event(
            event
        )

        # ------------------------------------------
        # INCIDENT MANAGEMENT
        # ------------------------------------------

        self._process_incident(
            alert=alert,
            object_id=object_id,
            object_class=object_class,
            zone_name=zone_name
        )

    # ======================================================
    # PROCESS INCIDENT
    # ======================================================

    def _process_incident(
        self,
        alert,
        object_id,
        object_class,
        zone_name
    ):
        """
        Create or update an incident associated with
        an analytical alert.
        """

        key = (
            object_id,
            zone_name
        )

        incident_id = (
            self.incident_states.get(
                key
            )
        )

        alert_status = alert.get(
            "status",
            "NORMAL"
        )

        priority = (
            self._map_alert_to_priority(
                alert_status
            )
        )

        reasons = alert.get(
            "reasons",
            []
        )

        if not isinstance(
            reasons,
            list
        ):

            reasons = (
                list(reasons)
                if reasons
                else []
            )

        # ------------------------------------------
        # CREATE NEW INCIDENT
        # ------------------------------------------

        if incident_id is None:

            incident = (
                self.incident_manager.create(
                    object_id=object_id,
                    object_class=object_class,
                    zone=zone_name,
                    priority=priority,
                    reasons=reasons
                )
            )

            if incident is None:

                return

            incident_id = incident.get(
                "id"
            )

            if incident_id is None:

                return

            self.incident_states[
                key
            ] = incident_id

            print(
                "[INCIDENT] "
                f"CREATED | "
                f"ID={incident_id} | "
                f"OBJECT={object_id} | "
                f"ZONE={zone_name} | "
                f"STATUS={incident.get('status', 'UNKNOWN')}"
            )

            return

        # ------------------------------------------
        # UPDATE EXISTING INCIDENT
        # ------------------------------------------

        incident = (
            self.incident_manager.update(
                incident_id=incident_id,
                priority=priority,
                reasons=reasons
            )
        )

        if incident is not None:

            print(
                "[INCIDENT] "
                f"UPDATED | "
                f"ID={incident.get('id', incident_id)} | "
                f"STATUS={incident.get('status', 'UNKNOWN')}"
            )

    # ======================================================
    # MAP ALERT TO PRIORITY
    # ======================================================

    @staticmethod
    def _map_alert_to_priority(
        alert_status
    ):
        """
        Map alert state to analytical incident priority.
        """

        mapping = {
            "NORMAL": "NORMAL",
            "SUSPICIOUS": "MEDIUM",
            "ALERT": "HIGH"
        }

        return mapping.get(
            alert_status,
            "LOW"
        )

    # ======================================================
    # REMOVE STALE ANOMALY STATES
    # ======================================================

    def _remove_stale_anomaly_states(
        self,
        active_ids
    ):
        """
        Remove behavior state for tracks that disappeared.
        """

        stale_keys = [
            key
            for key in self.anomaly_states
            if key[0] not in active_ids
        ]

        for key in stale_keys:

            del self.anomaly_states[
                key
            ]

    # ======================================================
    # REMOVE STALE ALERT STATES
    # ======================================================

    def _remove_stale_alert_states(
        self,
        active_ids
    ):
        """
        Remove analytical alert state for inactive tracks.
        """

        stale_keys = [
            key
            for key in self.alert_states
            if key[0] not in active_ids
        ]

        for key in stale_keys:

            del self.alert_states[
                key
            ]

    # ======================================================
    # REMOVE STALE INCIDENT STATES
    # ======================================================

    def _remove_stale_incident_states(
        self,
        active_ids
    ):
        """
        Resolve local incident references when the
        corresponding track disappears.
        """

        stale_keys = [
            key
            for key in self.incident_states
            if key[0] not in active_ids
        ]

        for key in stale_keys:

            incident_id = (
                self.incident_states.pop(
                    key
                )
            )

            try:

                resolved = (
                    self.incident_manager.resolve(
                        incident_id
                    )
                )

            except Exception as error:

                print(
                    "[INCIDENT ERROR] "
                    f"Could not resolve "
                    f"{incident_id}: "
                    f"{error}"
                )

                continue

            if resolved is not None:

                print(
                    "[INCIDENT] "
                    f"RESOLVED | "
                    f"ID={resolved.get('id', incident_id)} | "
                    f"OBJECT={resolved.get('object_id', key[0])} | "
                    f"ZONE={resolved.get('zone', key[1])}"
                )

    # ======================================================
    # SAVE EVENT
    # ======================================================

    def _save_event(
        self,
        event
    ):
        """
        Persist an event without allowing a database
        failure to terminate the vision pipeline.
        """

        if not isinstance(
            event,
            dict
        ):
            return

        try:
            self.database.insert_event(
                event
            )

        except Exception as error:
            print(
                "[DATABASE ERROR] "
                f"{type(error).__name__}: "
                f"{error}"
            )

    # ======================================================
    # DRAW ZONES
    # ======================================================

    def _draw_zones(
        self,
        frame
    ):
        """
        Draw configured spatial zones.
        """

        for zone in self.zones:

            try:

                cv2.rectangle(
                    frame,
                    (zone.x1, zone.y1),
                    (zone.x2, zone.y2),
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    str(zone.name),
                    (
                        zone.x1,
                        max(
                            zone.y1 - 10,
                            20
                        )
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

            except Exception:

                continue

    # ======================================================
    # DRAW METRICS
    # ======================================================

    def _draw_metrics(
        self,
        frame
    ):
        """
        Draw system performance metrics.
        """

        metrics = (
            self.metrics.snapshot()
        )

        if not isinstance(
            metrics,
            dict
        ):

            return

        fps = self._safe_float(
            metrics.get(
                "fps",
                0.0
            )
        )

        inference_ms = self._safe_float(
            metrics.get(
                "inference_ms",
                0.0
            )
        )

        cpu_percent = self._safe_float(
            metrics.get(
                "cpu_percent",
                0.0
            )
        )

        memory_mb = self._safe_float(
            metrics.get(
                "memory_mb",
                0.0
            )
        )

        active_objects = int(
            self._safe_float(
                metrics.get(
                    "active_objects",
                    0
                )
            )
        )

        total_events = int(
            self._safe_float(
                metrics.get(
                    "total_events",
                    0
                )
            )
        )

        lines = [
            f"FPS: {fps:.1f}",
            f"Inference: {inference_ms:.1f} ms",
            f"CPU: {cpu_percent:.1f}%",
            f"RAM: {memory_mb:.0f} MB",
            f"Objects: {active_objects}",
            f"Events: {total_events}",
        ]

        x = 20
        y = 30

        for line in lines:

            cv2.putText(
                frame,
                line,
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )

            y += 22

    # ======================================================
    # SAFE FLOAT
    # ======================================================

    @staticmethod
    def _safe_float(
        value,
        default=0.0
    ):
        """
        Safely convert a value to float.
        """

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return float(
                default
            )

    # ======================================================
    # STOP
    # ======================================================

    def stop(self):
        """
        Safely shut down all application resources.

        The method is intentionally idempotent so it can
        safely be called from finally blocks.
        """

        if self._stopped:

            return

        self._running = False

        print()

        print(
            "[SYSTEM] "
            "Stopping TacticalVision..."
        )

        self.tactical_state.set_system_status(
            "STOPPING"
        )

        # ------------------------------------------
        # CAMERA
        # ------------------------------------------

        try:

            dashboard_state.set_status("STOPPING")

            self.camera.release()

        except Exception as error:

            print(
                "[SYSTEM] "
                f"Camera release error: "
                f"{error}"
            )

        # ------------------------------------------
        # DATABASE
        # ------------------------------------------

        try:

            self.database.close()

        except Exception as error:

            print(
                "[SYSTEM] "
                f"Database close error: "
                f"{error}"
            )

        # ------------------------------------------
        # OPENCV
        # ------------------------------------------

        try:

            cv2.destroyAllWindows()

        except Exception as error:

            print(
                "[SYSTEM] "
                f"OpenCV shutdown error: "
                f"{error}"
            )

        # ------------------------------------------
        # FINAL STATE
        # ------------------------------------------

        self.tactical_state.set_system_status(
            "STOPPED"
        )

        dashboard_state.set_status("STOPPED")

        self._stopped = True

        print(
            "[SYSTEM] "
            "Shutdown complete."
        )
