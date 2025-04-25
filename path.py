from node import *
from graph import *

class Path:

    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        self.nodes = []

def AddNodeToPath(pth, Node):
    if Node in pth.nodes:
        return False
    else:
        pth.nodes.append(Node)
        return True
    
def ContainsNode(pth, Node):
    if Node in pth.nodes:
        return True
    else:
        return False

def CosttoNode(pth, Node):

    if Node in pth.nodes:
        Node = pth.nodes[-1]
        totalcost = 0
        i = 0
        while pth.nodes[i + 1] != Node:
            totalcost += Distance(pth.nodes[i], pth.nodes[i + 1])
            i += 1
        return totalcost
    else:
        return -1

def PlotPath(Graph, pth):
    fig, ax = plt.subplots()

    # Dibujar los nodos
    for node in Graph.lnodes:
        ax.plot(node.Ox, node.Oy, 'ko')  # Dibujar el nodo como un punto
        ax.text(node.Ox + 0.1, node.Oy + 0.1, node.name, fontsize=12)  # Etiqueta del nodo

    # Dibujar los segmentos
    for segment in Graph.lsegments:
        ax.plot([segment.origin.Ox, segment.destination.Ox], [segment.origin.Oy, segment.destination.Oy], 'b-')

    # Dibujar el camino
    for i in range(len(pth.nodes) - 1):
        ax.plot([pth.nodes[i].Ox, pth.nodes[i + 1].Ox], [pth.nodes[i].Oy, pth.nodes[i + 1].Oy], 'r-', linewidth=2)

    plt.show()


    
