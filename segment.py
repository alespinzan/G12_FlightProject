from node import *
import math

class segment:
    def __init__ (self, name, origin, destination):
        self.name = name
        self.origin = origin
        self.destination = destination
        self.cost = math.sqrt((destination.Ox - origin.Ox)**2 + (destination.Oy - origin.Oy)**2)
     