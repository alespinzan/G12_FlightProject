from node import *
f = open("data.txt","r")
lineas = [line.strip() for line in f.readlines()]
f.close()
print(lineas)
i = 0
nodes = []
for i in range(len(lineas)):
   partes = lineas[i].split(",")
   nodes.append(node(partes[0], partes[1], partes[2]))

print(nodes)