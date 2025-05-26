#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import subprocess

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from airspace import AirSpace
from graph import Graph, AddNode, AddSegment
from node import node
from path import PlotPath
from kml_utils import *  # graph_to_kml, path_to_kml

# --------------------------------------------------
# Rutas de datos
# --------------------------------------------------
BASE_DIR = os.path.dirname(__file__)

# Espacio Catalunya
NAV_CAT = os.path.join(BASE_DIR, "Cat_nav.txt")
SEG_CAT = os.path.join(BASE_DIR, "Cat_seg.txt")
AER_CAT = os.path.join(BASE_DIR, "Cat_aer.txt")

# Espacio España
NAV_ES = os.path.join(BASE_DIR, "Spain_nav.txt")
SEG_ES = os.path.join(BASE_DIR, "Spain_seg.txt")
AER_ES = os.path.join(BASE_DIR, "Spain_aer.txt")

# Espacio Europa
NAV_EU = os.path.join(BASE_DIR, "ECAC_nav.txt")
SEG_EU = os.path.join(BASE_DIR, "ECAC_seg.txt")
AER_EU = os.path.join(BASE_DIR, "ECAC_aer.txt")

# Variables globales
target_graph: Graph = None
last_path = None  # para redraw del último shortest path

# --------------------------------------------------
# Construcción de grafo desde AirSpace
# --------------------------------------------------
def build_from_airspace(nav, seg, aer) -> Graph:
    aspace = AirSpace()
    aspace.load_navpoints(nav)
    aspace.load_navsegments(seg)
    aspace.load_airports(aer)
    g = Graph()
    for np_obj in aspace.navpoints.values():
        AddNode(g, node(np_obj.name, np_obj.longitude, np_obj.latitude))
    for sg in aspace.navsegments:
        seg_name = f"{sg.origin.name}-{sg.destination.name}"
        AddSegment(g, seg_name, sg.origin.name, sg.destination.name)
    return g

# --------------------------------------------------
# Dibujo del grafo en el frame derecho
# --------------------------------------------------
def draw_graph(g: Graph, path=None):
    global target_graph, last_path
    target_graph = g
    last_path = path

    # figura más grande para aprovechar espacio
    fig = plt.Figure(figsize=(10, 10), dpi=100)
    ax = fig.add_subplot(1, 1, 1)

    # dibujar todos los nodos/segmentos
    from graph import DrawBaseGraph
    DrawBaseGraph(g, ax)
    # si hay camino mínimo, lo sobrepinta
    if path:
        PlotPath(g, path, ax)

    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.set_title("Visualización de Grafo")
    ax.grid(True, linestyle="--", linewidth=0.3)

    # incrustar en Tk (usando grid para expandir en ambos ejes)
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.grid(row=0, column=0, sticky="nsew")

# --------------------------------------------------
# Refrescar listado de nodos en Listbox
# --------------------------------------------------
def refresh_node_list():
    list_nodes.delete(0, tk.END)
    if not target_graph:
        return
    for nd in target_graph.lnodes:
        list_nodes.insert(tk.END, nd.name)

# --------------------------------------------------
# Carga de catálogos predefinidos
# --------------------------------------------------
def load_catalunya():
    global target_graph
    target_graph = build_from_airspace(NAV_CAT, SEG_CAT, AER_CAT)
    refresh_node_list()
    draw_graph(target_graph)

def load_espana():
    global target_graph
    target_graph = build_from_airspace(NAV_ES, SEG_ES, AER_ES)
    refresh_node_list()
    draw_graph(target_graph)

def load_europa():
    global target_graph
    target_graph = build_from_airspace(NAV_EU, SEG_EU, AER_EU)
    refresh_node_list()
    draw_graph(target_graph)

# --------------------------------------------------
# Carga/guardado genérico desde fichero
# --------------------------------------------------
def load_from_file():
    global target_graph
    path = filedialog.askopenfilename(filetypes=[("Gráfo TXT","*.txt")])
    if not path:
        return
    from graph import readfile
    try:
        target_graph = readfile(path)
    except Exception as e:
        messagebox.showerror("Error al leer", str(e))
        return
    refresh_node_list()
    draw_graph(target_graph)


def save_to_file():
    if not target_graph:
        messagebox.showinfo("Nada que guardar", "Carga o crea un grafo primero.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".txt",
        filetypes=[("Gráfo TXT","*.txt")])
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            for n in target_graph.lnodes:
                f.write(f"N {n.name} {n.Ox} {n.Oy}\n")
            for s in target_graph.lsegments:
                f.write(f"S {s.name} {s.origin.name} {s.destination.name}\n")
    except Exception as e:
        messagebox.showerror("Error al guardar", str(e))
    else:
        messagebox.showinfo("Guardado", f"Grafo guardado en:\n{path}")

# --------------------------------------------------
# Añadir / borrar nodos y segmentos
# --------------------------------------------------
def add_node():
    if not target_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    nombre = simpledialog.askstring("Nuevo nodo", "Nombre:")
    if not nombre:
        return
    try:
        lon = float(simpledialog.askstring("Coordenada","Longitud:"))
        lat = float(simpledialog.askstring("Coordenada","Latitud:"))
    except:
        messagebox.showerror("Error","Coordenadas inválidas")
        return
    if not AddNode(target_graph, node(nombre, lon, lat)):
        messagebox.showwarning("Aviso","El nodo ya existe")
    refresh_node_list()
    draw_graph(target_graph, last_path)

def del_node():
    sel = list_nodes.curselection()
    if not target_graph or not sel:
        messagebox.showinfo("Error","Selecciona un nodo")
        return
    nm = list_nodes.get(sel[0])
    # eliminar segmentos asociados
    target_graph.lsegments = [
        s for s in target_graph.lsegments
        if s.origin.name != nm and s.destination.name != nm
    ]
    target_graph.lnodes = [n for n in target_graph.lnodes if n.name != nm]
    refresh_node_list()
    draw_graph(target_graph)

def add_segment():
    if not target_graph or len(target_graph.lnodes) < 2:
        messagebox.showinfo("Error","Grafo inaccesible o sin nodos suficientes")
        return
    origin = simpledialog.askstring("Nuevo segmento","Nodo origen:")
    dest = simpledialog.askstring("Nuevo segmento","Nodo destino:")
    if origin not in [n.name for n in target_graph.lnodes] or \
       dest not in [n.name for n in target_graph.lnodes]:
        messagebox.showerror("Error","Nodo inválido")
        return
    name = f"{origin}-{dest}"
    if not AddSegment(target_graph, name, origin, dest):
        messagebox.showwarning("Aviso","Segmento no añadido")
    draw_graph(target_graph, last_path)

def del_segment():
    if not target_graph:
        return
    name = simpledialog.askstring("Eliminar segmento","Nombre del segmento:")
    before = len(target_graph.lsegments)
    target_graph.lsegments = [s for s in target_graph.lsegments if s.name != name]
    if len(target_graph.lsegments) == before:
        messagebox.showinfo("Aviso","Segmento no encontrado")
    draw_graph(target_graph, last_path)

# --------------------------------------------------
# Vecinos, alcanzables y shortest path
# --------------------------------------------------
def show_neighbors():
    sel = list_nodes.curselection()
    if not target_graph or not sel:
        return
    nm = list_nodes.get(sel[0])
    neigh = target_graph.GetNeighbors(nm)
    messagebox.showinfo("Vecinos", "\n".join(neigh) or "(ninguno)")

def show_reachable():
    sel = list_nodes.curselection()
    if not target_graph or not sel:
        return
    nm = list_nodes.get(sel[0])
    reach = target_graph.GetReachable(nm)
    messagebox.showinfo("Alcanzables", "\n".join(reach) or "(ninguno)")

def shortest_path():
    sel = list_nodes.curselection()
    if not target_graph or not sel:
        return
    src = list_nodes.get(sel[0])
    dst = simpledialog.askstring("Shortest Path","Destino:")
    if not dst:
        return
    path = target_graph.findShortestPath(src, dst)
    if path:
        draw_graph(target_graph, path)
    else:
        messagebox.showinfo("Resultado","No existe ruta")

# --------------------------------------------------
# Exportar y abrir KML
# --------------------------------------------------
def export_kml(scope):
    if scope == "CAT":
        g = build_from_airspace(NAV_CAT, SEG_CAT, AER_CAT)
        fname = "kml_cat.kml"
    elif scope == "ESP":
        g = build_from_airspace(NAV_ES, SEG_ES, AER_ES)
        fname = "kml_esp.kml"
    else:
        g = build_from_airspace(NAV_EU, SEG_EU, AER_EU)
        fname = "kml_eur.kml"
    out = os.path.join(BASE_DIR, fname)
    graph_to_kml(g, out)
    messagebox.showinfo("KML generado", out)
    try:
        if sys.platform.startswith("win"):
            os.startfile(out)
        elif sys.platform == "darwin":
            subprocess.call(["open", out])
        else:
            subprocess.call(["xdg-open", out])
    except:
        pass

# --------------------------------------------------
# Abrir la vista actual en Google Earth
# --------------------------------------------------
def open_google_earth():
    global target_graph, last_path
    if not target_graph:
        messagebox.showwarning("Error", "No hay grafo cargado.")
        return
    out = os.path.join(BASE_DIR, "view.kml")
    if last_path:
        path_to_kml(target_graph, last_path, out)
    else:
        graph_to_kml(target_graph, out)
    try:
        if sys.platform.startswith("win"):
            os.startfile(out)
        elif sys.platform == "darwin":
            subprocess.call(["open", out])
        else:
            subprocess.call(["xdg-open", out])
    except Exception:
        messagebox.showerror("Error", "No se pudo abrir Google Earth.")

# --------------------------------------------------
# Construcción de la ventana principal
# --------------------------------------------------
root = tk.Tk()
root.title("Airspace Explorer v4")
# Tamaño inicial de ventana amplio
root.geometry("1800x900")

# Panel de controles izquierdo
ctrl = tk.Frame(root, width=300)
ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

# Panel de dibujo derecho
graph_frame = tk.Frame(root)
graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
# permitir al grid interno expandirse
graph_frame.grid_rowconfigure(0, weight=1)
graph_frame.grid_columnconfigure(0, weight=1)

# Listbox de nodos
tk.Label(ctrl, text="Nodos:").pack(anchor="w")
list_nodes = tk.Listbox(ctrl, height=15)
list_nodes.pack(fill=tk.X, pady=2)

# Botones de consulta
tk.Button(ctrl, text="Vecinos",      command=show_neighbors).pack(fill=tk.X)
tk.Button(ctrl, text="Alcanzables",  command=show_reachable).pack(fill=tk.X)
tk.Button(ctrl, text="Shortest Path",command=shortest_path).pack(fill=tk.X, pady=(0,10))

# Botones CRUD
tk.Button(ctrl, text="Añadir nodo",    command=add_node).pack(fill=tk.X)
tk.Button(ctrl, text="Borrar nodo",    command=del_node).pack(fill=tk.X)
tk.Button(ctrl, text="Añadir segmento",command=add_segment).pack(fill=tk.X)
tk.Button(ctrl, text="Borrar segmento",command=del_segment).pack(fill=tk.X, pady=(0,10))

# Botones carga/guardado
tk.Button(ctrl, text="Carga Cat",     command=load_catalunya).pack(fill=tk.X)
tk.Button(ctrl, text="Carga España",  command=load_espana).pack(fill=tk.X)
tk.Button(ctrl, text="Carga Europa",  command=load_europa).pack(fill=tk.X)
tk.Button(ctrl, text="Carga desde TXT",command=load_from_file).pack(fill=tk.X)
tk.Button(ctrl, text="Guardar grafo", command=save_to_file).pack(fill=tk.X, pady=(0,10))

# Botones KML
tk.Button(ctrl, text="KML Cataluña", command=lambda: export_kml("CAT")).pack(fill=tk.X)
tk.Button(ctrl, text="KML España",   command=lambda: export_kml("ESP")).pack(fill=tk.X)
tk.Button(ctrl, text="KML Europa",   command=lambda: export_kml("EUR")).pack(fill=tk.X)
tk.Button(ctrl, text="Abrir en Google Earth", command=open_google_earth).pack(fill=tk.X)

# Arranca la aplicación
root.mainloop()
