# airspace.py
from navpoint import NavPoint
from navsegment import NavSegment
from navairport import NavAirport
from graph import *

import matplotlib.pyplot as plt

class AirSpace:
    def __init__(self):
        self.navpoints = {}  # id -> NavPoint
        self.navsegments = []  # list of NavSegment
        self.airports = {}  # id -> NavAirport

    def load_navpoints(self, nav_file):
        self.nav_file = nav_file
        with open(nav_file) as f:
            for line in f:
                np = NavPoint.parse_line(line)
                self.navpoints[np.id] = np

    def load_navsegments(self, filepath: str):
        with open(filepath) as f:
            for line in f:
                seg = NavSegment.parse_line(line, self.navpoints)
                self.navsegments.append(seg)

    def load_airports(self, filepath: str):
        with open(filepath) as f:
            current_id = None
            sids = []
            stars = []
            for line in f:
                code = line.strip()
                if not code:
                    continue
                if '.' not in code:  # Es un aeropuerto (ej: LEIB)
                    # Si ya hay uno anterior, guárdalo
                    if current_id is not None:
                        self.airports[current_id] = NavAirport(
                            id=current_id,
                            name=current_id,
                            sids=sids,
                            stars=stars
                        )
                    # Nuevo aeropuerto
                    current_id = code
                    sids = []
                    stars = []
                elif code.endswith('.D'):
                    sids.append(code)
                elif code.endswith('.A'):
                    stars.append(code)
            # Guarda el último aeropuerto
            if current_id is not None:
                self.airports[current_id] = NavAirport(
                    id=current_id,
                    name=current_id,
                    sids=sids,
                    stars=stars
                )
       

    def build_graph(self) -> Graph:
        g = Graph()
        # add NavPoints as nodes
        for np_obj in self.navpoints.values():
            AddNode(g, node(np_obj.name, np_obj.longitude, np_obj.latitude))
        # add segments
        for seg in self.navsegments:
            seg_name = f"{seg.origin.name}-{seg.destination.name}"
            AddSegment(g, seg_name, seg.origin.name, seg.destination.name)
        return g

    def shortest_path(self, start_id: str, end_id: str):
        g = self.build_graph()
        return g.findShortestPath(start_id, end_id)

    def reachable_from(self, start_id: str):
        g = self.build_graph()
        return g.ExplorePaths(start_id)

    def neighbors(self, point_id: str):
        return [seg.destination.id for seg in self.navsegments if seg.origin.id == point_id] + \
               [seg.origin.id for seg in self.navsegments if seg.destination.id == point_id]

    def plot(self, show_airports: bool = True):
        # Draw NavPoints and NavSegments
        lats = [np_obj.latitude for np_obj in self.navpoints.values()]
        lons = [np_obj.longitude for np_obj in self.navpoints.values()]

        plt.figure(figsize=(8, 8))
        plt.scatter(lons, lats, s=10, label="NavPoints", alpha=0.6)

        for seg in self.navsegments:
            x = [seg.origin.longitude, seg.destination.longitude]
            y = [seg.origin.latitude, seg.destination.latitude]
            plt.plot(x, y, linewidth=0.5, alpha=0.5)

        plt.xlabel("Longitud")
        plt.ylabel("Latitud")
        plt.title("Espacio Aéreo de Cataluña")
        plt.legend(loc="best")
        plt.axis("equal")
        plt.show()

    def find_shortest_path_any(self, start_id: str, end_id: str):
        """
        Encuentra el camino más corto entre dos aeropuertos (por sus SIDs/STARs) o entre NavPoints.
        """
        g = self.build_graph()

        # Si start_id es aeropuerto, usar sus SIDs como posibles orígenes
        if start_id in self.airports:
            start_points = self.airports[start_id].sids or self.airports[start_id].stars
        else:
            start_points = [start_id]

        # Si end_id es aeropuerto, usar sus STARs como posibles destinos
        if end_id in self.airports:
            end_points = self.airports[end_id].stars or self.airports[end_id].sids
        else:
            end_points = [end_id]

        best_path = None
        best_cost = float('inf')
        for s in start_points:
            for e in end_points:
                path = g.findShortestPath(s, e)
                if path and hasattr(path, 'cost') and path.cost < best_cost:
                    best_path = path
                    best_cost = path.cost
        return best_path

