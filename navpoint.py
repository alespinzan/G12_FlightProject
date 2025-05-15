class NavPoint:
    def __init__(self, id: str, name: str, latitude: float, longitude: float):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def parse_line(cls, line: str):
        line = line.strip()
        # si contiene comas, lo partimos por comas; si no, por espacios
        if ',' in line:
            parts = line.split(',')
        else:
            parts = line.split()
        if len(parts) < 4:
            raise ValueError(f"Invalid NavPoint line: {line}")
        # asumimos: ID, NAME, LAT, LON en las cuatro primeras posiciones
        id_, name, lat, lon = parts[0], parts[1], parts[2], parts[3]
        return cls(id_, name, float(lat), float(lon))
