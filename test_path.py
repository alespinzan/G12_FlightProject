from path import *
from node import *
from graph import *
from test_graph import *



startNode = G.lnodes[8]  # Cambia el índice según el nodo inicial deseado

possible_paths = ExplorePaths(startNode)
# Graficar todos los caminos en un solo grafo
PlotPaths(G, possible_paths)

shortest_path = findShortestPath(G, startNode, G.lnodes[5])

print(shortest_path.name, "Cost:", shortest_path.cost)

PlotPath(G, shortest_path)



