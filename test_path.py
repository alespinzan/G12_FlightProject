from path import *
from node import *
from graph import *
from test_graph import *




possible_paths = ExplorePaths(G, "A")
# Graficar todos los caminos en un solo grafo
PlotPaths(G, possible_paths)

shortest_path = findShortestPath(G, "A","B")

print(shortest_path.name, "Cost:", shortest_path.cost)

PlotPath(G, shortest_path)



