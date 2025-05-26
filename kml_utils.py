import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import simplekml

def path_to_kml(graph, path_obj, out_path):
    """
    Exporta solo los segmentos que recorren 'path_obj' (iterable de nodos
    o de nombres), y salva el resultado en out_path.
    """
    # 1) Extrae los nombres en una lista de strings
    if hasattr(path_obj, "nodes"):
        raw = path_obj.nodes
    else:
        raw = list(path_obj)
    path_names = [n.name if hasattr(n, "name") else n for n in raw]

    # 2) Construye un diccionario para lookup rápido
    node_map = {n.name: n for n in graph.lnodes}

    kml = simplekml.Kml()
    # 3) Itera por pares consecutivos y solo dibuja si ambos existen
    for u_name, v_name in zip(path_names, path_names[1:]):
        u = node_map.get(u_name)
        v = node_map.get(v_name)
        if u is None or v is None:
            # opcional: avisar o loggear qué nodo falta
            print(f"[WARNING] Nodo no encontrado en grafo: {u_name} o {v_name}")
            continue

        coords = [(u.Ox, u.Oy), (v.Ox, v.Oy)]
        ls = kml.newlinestring(name=f"{u_name} → {v_name}", coords=coords)
        ls.style.linestyle.width = 3
        ls.style.linestyle.color = simplekml.Color.red

    kml.save(out_path)
