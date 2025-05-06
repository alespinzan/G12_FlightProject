from node import *
import matplotlib.pyplot as plt


class Path:
    def __init__(self):
        self.name = ""
        self.cost = 0.0
        self.nodes = []

def AddNodeToPath(pth, Node):
   if len(pth.nodes) == 0: # If the Path is empty, add the Node to the Path.
       if Node in pth.nodes:
           return False
       else:
           pth.nodes.append(Node)
           return True
   else: # If the Path is not empty, check if the Node is a neighbor of the last node in the Path.
       if Node in pth.nodes:
           return False
       else:
           lastnode = pth.nodes[-1]
           if Node in lastnode.nl:
               pth.nodes.append(Node)
               return True
    
def ContainsNode(pth, Node): # Returns True if the Node is in the Path and False otherwise. 
    if Node in pth.nodes:
        return True
    else:
        return False

def CosttoNode(pth, Node): # Returns the total cost from the origin of the Path to the Node. Returns -1 if the Node is not in the Path. 

    if Node in pth.nodes:
        Node = pth.nodes[-1]
        totalcost = 0
        i = 0
        while i < len(pth.nodes) - 1 and pth.nodes[i] != Node:
            totalcost += Distance(pth.nodes[i], pth.nodes[i + 1])
            i += 1
        return totalcost
    else:
        return -1  
    
def ExplorePaths(g, startName):
    
    startNode = None

    for node in g.lnodes:
        if node.name == startName:
            startNode = node
            break
        else:
            startNode = False
    
    paths = []  # Lista para almacenar los caminos posibles
    stack = []  # Pila para manejar los nodos y caminos pendientes de explorar

    # Inicializar la pila con el nodo inicial y un camino vacío
    initial_path = Path()
    stack.append((initial_path, startNode))

    while len(stack) > 0:
        # Obtener el último elemento de la pila
        currentPath, currentNode = stack.pop()

        # Agregar el nodo actual al camino
        if not ContainsNode(currentPath, currentNode):
            AddNodeToPath(currentPath, currentNode)
        
        # Guardar una copia del camino actual
        new_path = Path()
        new_path.nodes = currentPath.nodes.copy()
        new_path.name = " -> ".join([node.name for node in new_path.nodes])
        new_path.cost = CosttoNode(currentPath, currentNode)
        paths.append(new_path)

        # Agregar los vecinos del nodo actual a la pila
        for neighbor in currentNode.nl:
            if not ContainsNode(currentPath, neighbor):  # Evitar ciclos
                # Crear una copia del camino actual para explorar el vecino
                new_path_copy = Path()
                new_path_copy.nodes = currentPath.nodes.copy()
                stack.append((new_path_copy, neighbor))

    return paths

def PlotPath(Graph, pth):
    fig, ax = plt.subplots()

    # Dibujar los nodos del grafo
    for node in Graph.lnodes:
        ax.plot(node.Ox, node.Oy, 'ko')  # Dibujar el nodo como un punto
        ax.text(node.Ox + 0.1, node.Oy + 0.1, node.name, fontsize=12)  # Etiqueta del nodo

    # Dibujar los segmentos del grafo
    for segment in Graph.lsegments:
        ax.plot([segment.origin.Ox, segment.destination.Ox], 
                [segment.origin.Oy, segment.destination.Oy], 'b-', zorder=2)  # Líneas azules para los segmentos

    # Dibujar el camino con flechas (encima de los segmentos)
    for i in range(len(pth.nodes) - 1):
        start = pth.nodes[i]
        end = pth.nodes[i + 1]
        OxStart, OyStart = start.Ox, start.Oy
        OxEnd, OyEnd = end.Ox, end.Oy
        dx = OxEnd - OxStart
        dy = OyEnd - OyStart
        ax.annotate(
            '',  # Sin texto
            xy=(OxEnd, OyEnd),  # Coordenadas del destino
            xytext=(OxStart, OyStart),  # Coordenadas del origen
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5)  # Estilo de la flecha
        )

    # Activar la cuadrícula
    ax.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5, zorder = 1)

    plt.show()

def PlotPaths(Graph, paths):
   
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    # Dibujar los nodos del grafo
    for node in Graph.lnodes:
        ax.plot(node.Ox, node.Oy, 'ko')  # Dibujar el nodo como un punto
        ax.text(node.Ox + 0.1, node.Oy + 0.1, node.name, fontsize=12)  # Etiqueta del nodo

    # Dibujar los segmentos del grafo
    for segment in Graph.lsegments:
        ax.plot([segment.origin.Ox, segment.destination.Ox], 
                [segment.origin.Oy, segment.destination.Oy], 'b-', zorder=2)  # Líneas azules para los segmentos

    # Dibujar todos los caminos con colores diferentes
    colors = ['r', 'g', 'c', 'm', 'y']  # Colores para los caminos
    for i, pth in enumerate(paths):
        color = colors[0]  # Seleccionar un color cíclicamente
        for j in range(len(pth.nodes) - 1):
            start = pth.nodes[j]
            end = pth.nodes[j + 1]
            dx_start, dy_start = start.Ox, start.Oy
            dx_end, dy_end = end.Ox, end.Oy
            ax.annotate(
            '',  # Sin texto
            xy=(dx_end, dy_end),  # Coordenadas del destino
            xytext=(dx_start, dy_start),  # Coordenadas del origen
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5)  # Estilo de la flecha
        )

    # Activar la cuadrícula
    ax.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5, zorder=1)

    plt.show()