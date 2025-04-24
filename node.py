import math

class node:
    def __init__ (self, name, Ox, Oy):
        self.name = name
        self.Ox = Ox
        self.Oy = Oy
        self.nl = []

def AddNeighbor(n1, n2):   
    if n2 in n1.nl:
        return False
    else:
        n1.nl.append(n2)
        return True
       
def Distance(n1, n2):
    return math.sqrt((n2.Ox - n1.Ox)**2 + (n2.Oy - n1.Oy)**2)