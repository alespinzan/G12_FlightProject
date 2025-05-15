class NavAirport:
    def __init__(self, id: str, name: str, sids: list, stars: list):
        self.id = id
        self.name = name
        self.sids = sids
        self.stars = stars

    @classmethod
    def parse_line(cls, line: str):
        line = line.strip()
        # Saltar líneas vacías o comentarios
        if not line or line.startswith('#'):
            return None
        # Separar por comas o espacios
        parts = line.split(',') if ',' in line else line.split()
        # Se necesitan al menos 4 campos: id, name, sids, stars
        if len(parts) < 4:
            # No es un registro completo, omitir
            return None
        id_, name = parts[0], parts[1]
        sids = parts[2].split('|') if parts[2] else []
        stars = parts[3].split('|') if parts[3] else []
        return cls(id_, name, sids, stars)