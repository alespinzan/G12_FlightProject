from path import *
from segment import *
from node import *
import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
        self.lnodes = []
        self.lsegments = []

    def GetNeighbors(self, node_name: str) -> list[str]:
        # find the node object
        node_obj = next((n for n in self.lnodes if n.name == node_name), None)
        if not node_obj:
            return []
        # return the names of its neighbors
        return [nbr.name for nbr in node_obj.nl]

    def findShortestPath(self, origin_name, dest_name):
        # delega en la función libre
        from graph import findShortestPath as _fsp
        return _fsp(self, origin_name, dest_name)

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
    nameSegment = nameOrigin + "-" + nameDestination
    seg = segment(nameSegment, Orig, Dest)
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

def DrawBaseGraph(g, ax):
        for node in g.lnodes:
            ax.plot(node.Ox, node.Oy, 'ko', markersize=3)  # Cambia el tamaño con markersize
            ax.text(node.Ox + 0.01, node.Oy + 0.01, node.name, fontsize=5.5)

def drawsegment(g, ax):

    DrawBaseGraph(g, ax)  # Llama a la función para dibujar los nodos

    for segment in g.lsegments:
            x_start, y_start = segment.origin.Ox, segment.origin.Oy
            x_end, y_end = segment.destination.Ox, segment.destination.Oy

            # Dibujar una flecha para el segmento
            ax.annotate(
                '',  # Sin texto
                xy=(x_end, y_end), # Coordenadas del destino
                xytext=(x_start, y_start),  # Coordenadas del origen
                arrowprops=dict(arrowstyle='->', color='c', lw=1)  # Estilo de la flecha
            )

            # Etiqueta del costo en el medio del segmento
            mid_x = (x_start + x_end) / 2
            mid_y = (y_start + y_end) / 2
            # ax.text(mid_x, mid_y, f"{segment.cost:.2f}", fontsize=5, color='black', ha='center')



def Plot(g):
    fig, ax = plt.subplots()  

    # Call DrawBaseGraph to utilize it
    DrawBaseGraph(g, ax)

    # Configuración de los ejes y título
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title('Graph Visualization with Arrows')
    ax.grid(False, linestyle='--', linewidth=0.5, color='red')
    plt.show()
    
def PlotNode(g, nameOrigin, ax):
    origin_node = None
    for node in g.lnodes:
        if node.name == nameOrigin:
            origin_node = node
            break

    if origin_node is None:
        return False

    for node in g.lnodes:
        if node == origin_node:
            ax.plot(node.Ox, node.Oy, 'bo')
            ax.text(node.Ox + 0.001, node.Oy + 0.001, node.name, fontsize=10)
        elif node in origin_node.nl:
            ax.plot(node.Ox, node.Oy, 'go')
            ax.text(node.Ox + 0.001, node.Oy + 0.001, node.name, fontsize=10)

    for segment in g.lsegments:
        if segment.origin == origin_node:
            x_values = [segment.origin.Ox, segment.destination.Ox]
            y_values = [segment.origin.Oy, segment.destination.Oy]
            ax.plot(x_values, y_values, 'r-')
            mid_x = (segment.origin.Ox + segment.destination.Ox) / 2
            mid_y = (segment.origin.Oy + segment.destination.Oy) / 2
            ax.text(mid_x, mid_y, f"{segment.cost:.2f}", fontsize=10, color='black', ha='center')

    # No plt.show() aquí
    return True

def readfile(filename):
    gr = Graph()

    with open(filename, "r") as f:
        for line in f:
            parts = line.strip().split()
            if not parts or parts[0].startswith("//"):
                continue  # Saltar líneas vacías o comentarios
            if parts[0] == "N" and len(parts) == 4:
                name = parts[1]
                x = float(parts[2])
                y = float(parts[3])
                AddNode(gr, node(name, x, y))
            elif parts[0] == "S" and len(parts) == 4:
                nameSegment = parts[1]
                nameOrigin = parts[2]
                nameDestination = parts[3]
                AddSegment(gr, nameSegment, nameOrigin, nameDestination)
    return gr

def deleteNode(g, node_name):
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

def findShortestPath(g, nameOrigin, nameDestination):
    foundOr = False
    foundDest = False
    i = 0
    while i < len(g.lnodes) and not foundOr:
        if g.lnodes[i].name == nameOrigin:
            foundOr = True
        else:
            i += 1
    if not foundOr:
        return None
    origin = g.lnodes[i]
    d = 0
    while d < len(g.lnodes) and not foundDest:
        if g.lnodes[d].name == nameDestination:
            foundDest = True
        else:
            d += 1
    if not foundDest:
        return None
    destination = g.lnodes[d]

    evpaths = []
    initial_path = Path()
    initial_path.nodes.append(origin)
    initial_path.cost = 0
    evpaths.append(initial_path)

    visited = set()  # <--- Añadido

    while len(evpaths) > 0:
        evpaths.sort(key=lambda p: p.cost + Distance(p.nodes[-1], destination))
        current_path = evpaths.pop(0)
        current_node = current_path.nodes[-1]

        # Si ya visitamos este nodo con menor o igual coste, saltar
        if (current_node.name in visited):
            continue
        visited.add(current_node.name)

        if current_node == destination:
            return current_path

        for neighbor in current_node.nl:
            if neighbor in current_path.nodes:
                continue
            new_path = Path()
            new_path.nodes = current_path.nodes.copy()
            new_path.nodes.append(neighbor)
            new_path.cost = current_path.cost + Distance(current_node, neighbor)
            evpaths.append(new_path)

    return None