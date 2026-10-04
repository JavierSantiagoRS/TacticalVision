class Zone:
    def __init__(self, name, x1, y1, x2, y2):
        self.name = name

        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)

    def contains(self, x, y):
        return (
            self.x1 <= x <= self.x2
            and self.y1 <= y <= self.y2
        )

    def draw(self, frame):
        import cv2

        cv2.rectangle(
            frame,
            (self.x1, self.y1),
            (self.x2, self.y2),
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            self.name,
            (self.x1, max(self.y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )


class ZoneManager:
    def __init__(self):
        self.zones = []

    def add_zone(self, zone):
        self.zones.append(zone)

    def get_zones(self):
        return self.zones

    def draw_all(self, frame):
        for zone in self.zones:
            zone.draw(frame)