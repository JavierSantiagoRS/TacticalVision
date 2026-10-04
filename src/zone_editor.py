import cv2

from src.zones import Zone


class ZoneEditor:
    def __init__(self):
        self.start_point = None
        self.current_point = None
        self.creating = False

        self.zone_counter = 1
        self.zones = []

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start_point = (x, y)
            self.current_point = (x, y)
            self.creating = True

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.creating:
                self.current_point = (x, y)

        elif event == cv2.EVENT_LBUTTONUP:
            if self.creating:
                self.current_point = (x, y)

                x1, y1 = self.start_point
                x2, y2 = self.current_point

                if abs(x2 - x1) > 20 and abs(y2 - y1) > 20:

                    zone = Zone(
                        f"ZONE_{self.zone_counter}",
                        x1,
                        y1,
                        x2,
                        y2
                    )

                    self.zones.append(zone)

                    self.zone_counter += 1

                self.start_point = None
                self.current_point = None
                self.creating = False

    def draw(self, frame):
        for zone in self.zones:
            zone.draw(frame)

        if self.creating and self.start_point and self.current_point:
            cv2.rectangle(
                frame,
                self.start_point,
                self.current_point,
                (0, 255, 255),
                2
            )