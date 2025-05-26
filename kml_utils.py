import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


def prettify(element):
    """Return a pretty-printed XML string for the Element."""
    rough = tostring(element, 'utf-8')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ")


def graph_to_kml(graph, filename):
    """
    Genera un archivo KML con todos los nodos y segmentos del grafo.
    - graph.lnodes: lista de nodos con atributos name, Ox, Oy
    - graph.lsegments: lista de segmentos con atributos name, origin.Ox, origin.Oy, destination.Ox, destination.Oy
    """
    # Crear raíz KML
    kml = Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    doc = SubElement(kml, 'Document')
    title = SubElement(doc, 'name')
    title.text = os.path.basename(filename)

    # Añadir nodos como Placemarks de tipo Point
    for n in graph.lnodes:
        pm = SubElement(doc, 'Placemark')
        name = SubElement(pm, 'name')
        name.text = n.name
        pt = SubElement(pm, 'Point')
        coords = SubElement(pt, 'coordinates')
        # longitud,latitud,altitud (usamos Ox como lon y Oy como lat)
        coords.text = f"{n.Ox},{n.Oy},0"

    # Añadir segmentos como Placemarks de tipo LineString
    for seg in graph.lsegments:
        pm = SubElement(doc, 'Placemark')
        name = SubElement(pm, 'name')
        name.text = seg.name
        ls = SubElement(pm, 'LineString')
        coords = SubElement(ls, 'coordinates')
        # texto de coordenadas separadas por espacio
        coords_list = []
        coords_list.append(f"{seg.origin.Ox},{seg.origin.Oy},0")
        coords_list.append(f"{seg.destination.Ox},{seg.destination.Oy},0")
        coords.text = ' '.join(coords_list)

    # Guardar en fichero
    xml_str = prettify(kml)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    print(f"Archivo KML generado: {filename}")


def path_to_kml(graph, path, filename):
    """
    Genera un KML que representa únicamente el camino dado (listado de nombres de nodos).
    """
    # Crear raíz KML
    kml = Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    doc = SubElement(kml, 'Document')
    title = SubElement(doc, 'name')
    title.text = os.path.basename(filename)

    # Obtener nodos del path
    coords_list = []
    for node_name in path:
        node_obj = next(n for n in graph.lnodes if n.name == node_name)
        coords_list.append(f"{node_obj.Ox},{node_obj.Oy},0")

    pm = SubElement(doc, 'Placemark')
    SubElement(pm, 'name').text = 'Camino mínimo'
    ls = SubElement(pm, 'LineString')
    coords = SubElement(ls, 'coordinates')
    coords.text = ' '.join(coords_list)

    xml_str = prettify(kml)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    print(f"Archivo KML de camino generado: {filename}")