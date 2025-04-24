from segment import *
from node import *
node1 = node("Node1", 0, 0)
node2 = node("Node2", 3, 4)
node3 = node("Node3", 6, 8)

segment1 = segment("a", node1, node2)
segment2 = segment("b", node2, node3)

print(segment1.name, segment1.origin.name, segment1.destination.name, segment1.cost)  
print(segment2.name, segment2.origin.name, segment2.destination.name, segment2.cost)  