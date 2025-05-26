#!/usr/bin/env python3
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from airspace import AirSpace
from graph import Graph, AddNode, AddSegment
from node import node

def prettify(element):
    """Devuelve un string XML con indentación."""
    rough = tostring(element, 'utf-8')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ")

def graph_to_kml(graph, filename):
    kml = Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    doc = SubElement(kml, 'Document')
    SubElement(doc, 'name').text = os.path.basename(filename)

    # Añadir nodos como Placemark→Point
    for n in graph.lnodes:
        pm = SubElement(doc, 'Placemark')
        SubElement(pm, 'name').text = n.name
        pt = SubElement(pm, 'Point')
        coords = SubElement(pt, 'coordinates')
        coords.text = f"{n.Ox},{n.Oy},0"

    # Añadir segmentos como Placemark→LineString
    for seg in graph.lsegments:
        pm = SubElement(doc, 'Placemark')
        SubElement(pm, 'name').text = seg.name
        ls = SubElement(pm, 'LineString')
        coords = SubElement(ls, 'coordinates')
        coords.text = (
            f"{seg.origin.Ox},{seg.origin.Oy},0 "
            f"{seg.destination.Ox},{seg.destination.Oy},0"
        )

    # Serializar y guardar
    xml_str = prettify(kml)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    print(f"KML generado: {filename}")

def main():
    base = os.path.dirname(__file__)
    NAV = os.path.join(base, "Spain_nav.txt")
    SEG = os.path.join(base, "Spain_seg.txt")
    AER = os.path.join(base, "Spain_aer.txt")

    # Carga del espacio aéreo de España
    aspace = AirSpace()
    aspace.load_navpoints(NAV)
    aspace.load_navsegments(SEG)
    aspace.load_airports(AER)

    # Construcción del grafo
    g = Graph()
    for np_obj in aspace.navpoints.values():
        AddNode(g, node(np_obj.name,
                        np_obj.longitude,
                        np_obj.latitude))
    for seg in aspace.navsegments:
        name = f"{seg.origin.name}-{seg.destination.name}"
        AddSegment(g, name,
                   seg.origin.name,
                   seg.destination.name)

    # Exportar a KML
    out = os.path.join(base, "espacio_espana.kml")
    graph_to_kml(g, out)

if __name__ == "__main__":
    main()
