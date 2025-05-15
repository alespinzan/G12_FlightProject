
# airspace.py
from navpoint import NavPoint
from navsegment import NavSegment
from navairport import NavAirport
from graph import Graph
import matplotlib.pyplot as plt

class AirSpace:
    def __init__(self):
        self.navpoints = {}  # id -> NavPoint
        self.navsegments = []  # list of NavSegment
        self.airports = {}  # id -> NavAirport

    def load_navpoints(self, filepath: str):
        with open(filepath) as f:
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
            for line in f:
                ap = NavAirport.parse_line(line)
                if ap:
                    self.airports[ap.id] = ap

    def build_graph(self) -> Graph:
        g = Graph()
        # add NavPoints as nodes
        for np_obj in self.navpoints.values():
            g.AddNode(np_obj.id, (np_obj.latitude, np_obj.longitude))
        # add segments
        for seg in self.navsegments:
            g.AddSegment(seg.origin.id, seg.destination.id, seg.distance)
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

