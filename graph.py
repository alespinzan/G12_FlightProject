from path import *
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
            ax.text(node.Ox + 0.1, node.Oy + 0.1, node.name, fontsize=7)

        # Dibujar los segmentos como flechas
        for segment in g.lsegments:
            x_start, y_start = segment.origin.Ox, segment.origin.Oy
            x_end, y_end = segment.destination.Ox, segment.destination.Oy

            # Dibujar una flecha para el segmento
            ax.annotate(
                '',  # Sin texto
                xy=(x_end, y_end), # Coordenadas del destino
                xytext=(x_start, y_start),  # Coordenadas del origen
                arrowprops=dict(arrowstyle='->', color='blue', lw=1)  # Estilo de la flecha
            )

            # Etiqueta del costo en el medio del segmento
            mid_x = (x_start + x_end) / 2
            mid_y = (y_start + y_end) / 2
            ax.text(mid_x, mid_y, f"{segment.cost:.2f}", fontsize=10, color='black', ha='center')

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
        if segment.origin == origin_node:
            x_values = [segment.origin.Ox, segment.destination.Ox]
            y_values = [segment.origin.Oy, segment.destination.Oy]

            ax.plot(x_values, y_values, 'r-')

            mid_x = (segment.origin.Ox + segment.destination.Ox) / 2
            mid_y = (segment.origin.Oy + segment.destination.Oy) / 2
            ax.text(mid_x, mid_y, f"{segment.cost:.2f}", fontsize=10, color='black', ha='center')

    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title(f'Graph Visualization: {nameOrigin} and Neighbors')
    ax.grid(True, linestyle='--', linewidth=0.5, color='red')
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
        for i in range(len(gr.lnodes)):    # Cambiar el addSegmet
            next_index = (i + 1) % len(gr.lnodes) 
            AddSegment(gr, gr.lnodes[i].name + "-" + gr.lnodes[next_index].name, gr.lnodes[i].name, gr.lnodes[next_index].name)
                
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
    origin = g.lnodes[i]
    d = 0
    while d < len(g.lnodes) and not foundDest:
        if g.lnodes[d].name == nameDestination:
            foundDest = True
        else:
            d += 1
    destination = g.lnodes[d]
   
    evpaths = []  # Lista de caminos
    initial_path = Path()  # Crear un camino inicial
    initial_path.nodes.append(origin)  # Agregar el nodo de origen al camino inicial
    initial_path.cost = 0  # El costo inicial es 0
    evpaths.append(initial_path)  # Agregar el camino inicial a la lista de caminos

    while len(evpaths) > 0:
        # Ordenar los caminos por costo estimado (costo actual + heurística)
        evpaths.sort(key=lambda p: p.cost + Distance(p.nodes[-1], destination))
        current_path = evpaths.pop(0)  # Remover el camino con el menor costo y guardarlo

        # Obtener el último nodo del camino actual
        current_node = current_path.nodes[-1]

        # Si el último nodo es el destino, devolver el camino actual
        if current_node == destination:
            return current_path

        # Explorar los vecinos del último nodo
        for neighbor in current_node.nl:
            # Si el vecino ya está en el camino actual, ignorarlo (evitar ciclos)
            if neighbor in current_path.nodes:
                continue

            # Crear un nuevo camino con el vecino
            new_path = Path()
            new_path.nodes = current_path.nodes.copy()
            new_path.nodes.append(neighbor)
            new_path.cost = current_path.cost + Distance(current_node, neighbor)

            # Agregar el nuevo camino a la lista de caminos
            evpaths.append(new_path)

    # Si la lista de caminos está vacía, no es posible llegar al destino
    return None