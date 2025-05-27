#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import subprocess

from airspace import *
from graph import *
from node import *
from path import PlotPath
from kml_utils import graph_to_kml

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
def draw_graph(g, pth=None, pths=None):
    # Limpia el frame de gráficos anterior
    for w in graph_frame.winfo_children():
        w.destroy()

    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    fig = plt.Figure(figsize=(10, 7))
    ax = fig.add_subplot(111)

    # Dibuja el grafo base siempre
    from graph import DrawBaseGraph
    DrawBaseGraph(g, ax)

    # Si hay un path, lo resalta encima
    if pth is not None:
        PlotPath(g, pth, ax)
    elif pths is not None:
        PlotPaths(g, pths, ax)

    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.set_title("Visualización de Grafo")
    ax.grid(True, linestyle='--', linewidth=0.3, color='gray')

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

def show_neighbors():
    if not target_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    sel = list_nodes.curselection()
    if not sel:
        messagebox.showinfo("Select a node", "Selecciona un nodo primero.")
        return
    name = list_nodes.get(sel[0])
    PlotNode(target_graph, name)

def show_reachable():
    if not target_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    start = simpledialog.askstring("Reachable", "Nodo inicio:")
    if start:
        r = ExplorePaths(target_graph, start)
        if r:
            draw_graph(target_graph, pths=r)
        else:
            messagebox.showinfo("Error", "Nodo no válido.")

def shortest_path():
    global target_graph, last_path
    if not target_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    start = simpledialog.askstring("Shortest Path", "Nodo inicio:")
    end = simpledialog.askstring("Shortest Path", "Nodo fin:")
    if start and end:
        path = findShortestPath(target_graph, start, end)
        if path:
            last_path = path
            draw_graph(target_graph, pth=path)
        else:
            messagebox.showinfo("Error", "No hay ruta.")

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
root.geometry("1200x700")

# Frames
ctrl = tk.Frame(root, width=300)
ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
graph_frame = tk.Frame(root)
graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


# Botonera (contenedor de botones y paneles de control)
buttons = tk.LabelFrame(ctrl, text="control")
buttons.pack(fill=tk.BOTH, expand=True)

# --- Carga de grafos ---
loadGraphFrame = tk.LabelFrame(buttons, text="Carga de grafos")
loadGraphFrame.grid(row=0, column=0, sticky="nswe", pady=3)
tk.Button(loadGraphFrame, text="Carga Cataluña", command=load_catalunya).grid(row=0, column=0, padx=2, pady=2)
tk.Button(loadGraphFrame, text="Carga España", command=load_espana).grid(row=0, column=1, padx=2, pady=2)
tk.Button(loadGraphFrame, text="Carga Europa", command=load_europa).grid(row=1, column=0, padx=2, pady=2)
tk.Button(loadGraphFrame, text="Carga desde TXT", command=load_from_file).grid(row=1, column=1, padx=2, pady=2)
tk.Button(loadGraphFrame, text="Guardar grafo", command=save_to_file).grid(row=2, column=0, columnspan=2, padx=2, pady=2)

# --- Operaciones sobre el grafo ---
graphOpsFrame = tk.LabelFrame(buttons, text="Operaciones sobre el grafo")
graphOpsFrame.grid(row=1, column=0, sticky="nswe", pady=3)
tk.Button(graphOpsFrame, text="Añadir nodo", command=add_node).grid(row=0, column=0, padx=2, pady=2)
tk.Button(graphOpsFrame, text="Borrar nodo", command=del_node).grid(row=0, column=1, padx=2, pady=2)
tk.Button(graphOpsFrame, text="Añadir segmento", command=add_segment).grid(row=1, column=0, padx=2, pady=2)
tk.Button(graphOpsFrame, text="Borrar segmento", command=del_segment).grid(row=1, column=1, padx=2, pady=2)

# --- Listado de nodos ---
nodesFrame = tk.LabelFrame(graphOpsFrame, text="Nodos")
nodesFrame.grid(row=2, column=0, columnspan=2, sticky="nswe", pady=2)
list_nodes = tk.Listbox(nodesFrame, height=7)
list_nodes.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

# --- Consultas ---
queryFrame = tk.LabelFrame(buttons, text="Consultas")
queryFrame.grid(row=2, column=0, sticky="nswe", pady=3)
tk.Button(queryFrame, text="Vecinos", command=show_neighbors).grid(row=0, column=0, padx=2, pady=2)
tk.Button(queryFrame, text="Alcanzables", command=show_reachable).grid(row=0, column=1, padx=2, pady=2)
tk.Button(queryFrame, text="Shortest Path", command=shortest_path).grid(row=1, column=0, columnspan=2, padx=2, pady=2)

# Botones KML
tk.Button(ctrl, text="KML Cataluña", command=lambda: export_kml("CAT")).pack(fill=tk.X)
tk.Button(ctrl, text="KML España",   command=lambda: export_kml("ESP")).pack(fill=tk.X)
tk.Button(ctrl, text="KML Europa",   command=lambda: export_kml("EUR")).pack(fill=tk.X)

# Arranca la aplicación
root.mainloop()
