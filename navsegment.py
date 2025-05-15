# navsegment.py
import math
from navpoint import NavPoint

class NavSegment:
    def __init__(self, id: str, origin: NavPoint, destination: NavPoint):
        self.id = id
        self.origin = origin
        self.destination = destination
        self.distance = self._compute_distance()

    @classmethod
    def parse_line(cls, line: str, lookup: dict):
        line = line.strip()
        # soportar coma o espacio
        parts = line.split(',') if ',' in line else line.split()
        # Cat_seg real tiene al menos 3 campos: origen, destino, coste
        if len(parts) < 3:
            raise ValueError(f"Invalid NavSegment line: {line}")
        origin_id = parts[0]
        dest_id   = parts[1]
        # (opcional) float(parts[2]) es el coste leído, pero lo calculamos desde coords
        origin = lookup.get(origin_id)
        dest   = lookup.get(dest_id)
        if origin is None or dest is None:
            raise KeyError(f"NavPoint IDs {origin_id} or {dest_id} not found")
        seg_id = f"{origin_id}-{dest_id}"
        return cls(seg_id, origin, dest)

    def _compute_distance(self):
        dx = self.origin.latitude - self.destination.latitude
        dy = self.origin.longitude - self.destination.longitude
        return math.hypot(dx, dy)
