import json
from pathlib import Path

from src.config import ZONES_PATH
from src.zones import Zone


class ZoneStorage:
    """
    Handles saving and loading configured detection zones.
    """

    def __init__(self, path=ZONES_PATH):
        self.path = Path(path)

    def save(self, zones):
        """
        Save a list of Zone objects to a JSON file.
        """

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = []

        for zone in zones:
            data.append({
                "name": zone.name,
                "x1": zone.x1,
                "y1": zone.y1,
                "x2": zone.x2,
                "y2": zone.y2
            })

        with open(
            self.path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                indent=4
            )

    def load(self):
        """
        Load zones from the JSON configuration file.

        Returns:
            list[Zone]: configured zones.
        """

        if not self.path.exists():
            return []

        try:
            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

        except (json.JSONDecodeError, OSError) as error:
            print(
                f"ERROR: No se pudieron cargar las zonas: {error}"
            )
            return []

        zones = []

        for item in data:
            try:
                zone = Zone(
                    name=item["name"],
                    x1=item["x1"],
                    y1=item["y1"],
                    x2=item["x2"],
                    y2=item["y2"]
                )

                zones.append(zone)

            except (KeyError, TypeError, ValueError) as error:
                print(
                    f"ADVERTENCIA: Zona inválida ignorada: {error}"
                )

        return zones