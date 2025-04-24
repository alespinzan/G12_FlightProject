from segment import *
from node import *
import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
        self.lnodes = []
        self.lsegments = []

def AddNode(g, n):
    if n in g.lnodes:
        return False
    else:
        g.lnodes.append(n)
        return True

def AddSegment(g, nameSegment, nameOrigin, nameDestination):
    foundOr = False
    foundDest = False
    i = 0
    while i < len(g.lnodes) and not foundOr:
        if g.lnodes[i].name == nameOrigin:
            foundOr = True
        else:
            i += 1
    Orig = g.lnodes[i]
    d = 0
    while d < len(g.lnodes) and not foundDest:
        if g.lnodes[d].name == nameDestination:
            foundDest = True
        else:
            d += 1
    Dest = g.lnodes[d]
    seg = segment(nameOrigin + "-" + nameDestination, Orig, Dest)
    seg.name = nameSegment
    g.lsegments.append(seg)
    AddNeighbor(Orig, Dest)
    if not foundOr or not foundDest:
        return False
    else:
        return True

def GetClosest(g, x, y):
    position = node("position", x, y)
    distances = []
    for i in range(len(g.lnodes)):
        distances.append(Distance(position, g.lnodes[i]))
    minDistance = min(distances)
    closestNode = g.lnodes[distances.index(minDistance)]
    return closestNode

def Plot(g):
    fig, ax = plt.subplots()

    for node in g.lnodes:
        ax.plot(node.Ox, node.Oy, 'o')
        ax.text(node.Ox + 0.1, node.Oy + 0.1, node.name, fontsize=12)

    for segment in g.lsegments:

        x_values = [segment.origin.Ox, segment.destination.Ox]
        y_values = [segment.origin.Oy, segment.destination.Oy]

        ax.plot(x_values, y_values, 'b-' )

        mid_x = (segment.origin.Ox + segment.destination.Ox) / 2
        mid_y = (segment.origin.Oy + segment.destination.Oy) / 2
        ax.text(mid_x, mid_y, f"{segment.cost:.2f}", fontsize=10, color='red', ha='center')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title('Graph Visualization')
    plt.legend()
    plt.grid(True)
    plt.show()
    
def PlotNode(g,nameOrigin):
    origin_node = None
    for node in g.lnodes:
        if node.name == nameOrigin:
            origin_node = node
            break

    if origin_node is None:

        return False

    fig, ax = plt.subplots()

    for node in g.lnodes:
        if node == origin_node:
            ax.plot(node.Ox, node.Oy, 'bo')
            ax.text(node.Ox + 0.1, node.Oy + 0.1, node.name, fontsize=10)
        elif node in origin_node.nl:
            ax.plot(node.Ox, node.Oy, 'go')
            ax.text(node.Ox + 0.1, node.Oy + 0.1, node.name, fontsize=10)
        else:
            ax.plot(node.Ox, node.Oy, 'ko')
            ax.text(node.Ox + 0.1, node.Oy + 0.1, node.name, fontsize=10)

    for segment in g.lsegments:
        if segment.origin == origin_node or segment.destination == origin_node:
            x_values = [segment.origin.Ox, segment.destination.Ox]
            y_values = [segment.origin.Oy, segment.destination.Oy]

            ax.plot(x_values, y_values, 'r-')

            mid_x = (segment.origin.Ox + segment.destination.Ox) / 2
            mid_y = (segment.origin.Oy + segment.destination.Oy) / 2
            ax.text(mid_x, mid_y, f"{segment.cost:.2f}", fontsize=10, color='red', ha='center')

    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title(f'Graph Visualization: {nameOrigin} and Neighbors')
    plt.grid(True)
    plt.show()
    return True

def readfile(filename):

    gr = Graph()

    with open(filename, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 3:
                name = parts[0].strip()
                x = float(parts[1])
                y = float(parts[2])
                AddNode(gr, node(name, x, y))
        for i in range(len(gr.lnodes)):
            next_index = (i + 1) % len(gr.lnodes)  # Wrap around to the start of the list
            AddSegment(gr, gr.lnodes[i].name + "-" + gr.lnodes[next_index].name, gr.lnodes[i].name, gr.lnodes[next_index].name)
                
    return gr

def delete_node(g, node_name):
    # Encontrar el nodo a eliminar
    node_to_delete = None
    for node in g.lnodes:
        if node.name == node_name:
            node_to_delete = node
            break

    if not node_to_delete:
        return False  # Nodo no encontrado

    # Eliminar el nodo de la lista de nodos
    g.lnodes.remove(node_to_delete)

    # Eliminar los segmentos asociados al nodo
    g.lsegments = [
        segment for segment in g.lsegments
        if segment.origin != node_to_delete and segment.destination != node_to_delete
    ]

    # Eliminar el nodo de las listas de vecinos de otros nodos
    for node in g.lnodes:
        if node_to_delete in node.nl:
            node.nl.remove(node_to_delete)

    return True  # Nodo eliminado con éxito

def closestPath(g, startNodeName, endNodeName):

    startNode = None
    endNode = None

    for i in g.lnodes:
        if node.name == startNodeName:
            startNode = g.lnodes[i]
            break
    for i in g.lnodes:
        if node.name == endNodeName:
            endNode = g.lnodes[i]
            break
    
    if not startNode or not endNode:
        return "path can't be defined"
    else:
        next
    
    paths = []
    paths.append()

    

