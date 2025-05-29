#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import subprocess
from PIL import Image, ImageTk
import matplotlib.image as mpimg
from airspace import *
from graph import *
from node import *
from path import PlotPath
from kml_utils import graph_to_kml, path_to_kml
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
current_graph: Graph = None
last_path = None
show_segments = False
selected_nodes = []
initial_xlim = None
initial_ylim = None
dark_mode = False
show_map_bg = False  # Controla si se muestra el mapa de fondo
# NUEVO: Estado de visualización actual
last_draw_type = None  # "path", "paths", "highlight", "base"
last_draw_data = None  # datos relevantes (lista de nodos, etc.)

# Construcción de grafo desde AirSpace

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
    g._airspace = aspace  # <-- Añade esto
    return g

# Dibujo del grafo en el frame derecho

def draw_graph(g, pth=None, pths=None, highlight_node=None):
    global last_draw_type, last_draw_data
    # Limpia el frame de gráficos anterior
    for w in graph_frame.winfo_children():
        w.destroy()

    fig = plt.Figure(figsize=(10, 7))
    ax = fig.add_subplot(111)

    # --- Imagen de fondo solo para Cataluña ---
   
    map_path = os.path.join(BASE_DIR, "imagenCat.png")
    if hasattr(g, "_airspace") and getattr(g._airspace, "nav_file", None) == NAV_CAT and show_map_bg:
        if os.path.exists(map_path):
            img = mpimg.imread(map_path)
            ax.imshow(img, extent=(-1.1, 4.3, 38.2, 42.0), aspect='auto', zorder=0)
        else:
            messagebox.showwarning("Aviso", "No se encontró la imagen de fondo 'imagenCat.png'.")
            use_bg = False

    # Dibuja el grafo base siempre
    
    DrawBaseGraph(g, ax)
    if show_segments:
        drawsegment(g, ax)

    # Si hay un path, lo resalta encima
    if pth is not None:
        PlotPath(g, pth, ax)
        last_draw_type = "path"
        # Soporta tanto objeto con .nodes como lista simple
        if hasattr(pth, "nodes"):
            last_draw_data = [n.name if hasattr(n, "name") else n for n in pth.nodes]
        else:
            last_draw_data = [n.name if hasattr(n, "name") else n for n in pth]
    elif pths is not None:
        PlotPaths(g, pths, ax)
        last_draw_type = "paths"
        last_draw_data = []
        for path in pths:
            if hasattr(path, "nodes"):
                last_draw_data.extend([n.name if hasattr(n, "name") else n for n in path.nodes])
            else:
                last_draw_data.extend([n.name if hasattr(n, "name") else n for n in path])
        last_draw_data = list(set(last_draw_data))
    elif highlight_node is not None:
        from graph import PlotNode
        PlotNode(g, highlight_node, ax)
        last_draw_type = "highlight"
        last_draw_data = [highlight_node]
    else:
        last_draw_type = "base"
        last_draw_data = [n.name for n in g.lnodes]

    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.set_title("Visualización de Grafo")
    ax.grid(True, linestyle='--', linewidth=0.3, color='gray')

    # Ajusta los márgenes del área de dibujo (izquierda, derecha, abajo, arriba)
    fig.subplots_adjust(left=0.07, right=0.96, bottom=0.08, top=0.95)

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.grid(row=0, column=0, sticky="nsew")

    # --- ZOOM con la rueda del ratón ---
    def zoom(event):
        # Solo responde a eventos sobre el eje
        if event.inaxes != ax:
            return
        scale_factor = 1.2 if event.button == 'up' else 1/1.2
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        new_width = (xlim[1] - xlim[0]) * scale_factor
        new_height = (ylim[1] - ylim[0]) * scale_factor
        relx = (xlim[1] - xdata) / (xlim[1] - xlim[0])
        rely = (ylim[1] - ydata) / (ylim[1] - ylim[0])
        ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        canvas.draw_idle()

    # Conecta el evento de scroll
    canvas.mpl_connect("scroll_event", zoom)

    def on_click(event):
        if event.inaxes != ax:
            return
        if event.button != 1:  # Solo botón izquierdo selecciona nodos
            return
        # Limita la selección a 2 nodos
        if len(selected_nodes) >= 2:
            messagebox.showinfo("Selección", "Solo puedes seleccionar hasta 2 nodos. Usa 'Limpiar selección' para reiniciar.")
            return
        # Encuentra el nodo más cercano al clic
        min_dist = float('inf')
        nearest = None
        for n in g.lnodes:
            dist = ((event.xdata - n.Ox)**2 + (event.ydata - n.Oy)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                nearest = n
        if nearest and min_dist < 0.2:  # Ajusta el umbral según escala
            if nearest.name not in selected_nodes:
                selected_nodes.append(nearest.name)
                # Resalta el nodo seleccionado
                ax.plot(nearest.Ox, nearest.Oy, 'ro', markersize=5)
                canvas.draw_idle()

    # Conecta el evento de clic
    canvas.mpl_connect("button_press_event", on_click)

    # Variables para pan
    pan_data = {"press": None, "xlim": None, "ylim": None}

    def on_press(event):
        if event.inaxes != ax or event.button != 2:  # Solo botón central
            return
        pan_data["press"] = (event.x, event.y)
        pan_data["xlim"] = ax.get_xlim()
        pan_data["ylim"] = ax.get_ylim()

    def on_release(event):
        if event.button == 2:
            pan_data["press"] = None

    def on_motion(event):
        if pan_data["press"] is None or event.inaxes != ax:
            return
        dx = event.x - pan_data["press"][0]
        dy = event.y - pan_data["press"][1]
        xlim = pan_data["xlim"]
        ylim = pan_data["ylim"]
        width = widget.winfo_width()
        height = widget.winfo_height()
        if width == 0 or height == 0:
            return
        dx_data = -dx * (xlim[1] - xlim[0]) / width
        dy_data = -dy * (ylim[1] - ylim[0]) / height  # Invertir el eje Y
        ax.set_xlim(xlim[0] + dx_data, xlim[1] + dx_data)
        ax.set_ylim(ylim[0] + dy_data, ylim[1] + dy_data)
        canvas.draw_idle()

    # Conecta los eventos de pan
    canvas.mpl_connect("button_press_event", on_press)
    canvas.mpl_connect("button_release_event", on_release)
    canvas.mpl_connect("motion_notify_event", on_motion)


def design_graph():
    global target_graph, last_path, selected_nodes
    target_graph = Graph()  # Grafo vacío
    last_path = None
    selected_nodes.clear()
    draw_graph(target_graph)

def load_example_graph():
    global target_graph, last_path, selected_nodes
    from test_graph import G  # Asegúrate de tener este archivo y objeto
    target_graph = G
    last_path = None
    selected_nodes.clear()
    draw_graph(target_graph)

# --------------------------------------------------
# Carga de catálogos predefinidos
# --------------------------------------------------
def load_catalunya():
    global target_graph
    target_graph = build_from_airspace(NAV_CAT, SEG_CAT, AER_CAT)
    draw_graph(target_graph)
    update_airport_listbox()

def load_espana():
    global target_graph
    target_graph = build_from_airspace(NAV_ES, SEG_ES, AER_ES)
    draw_graph(target_graph)
    update_airport_listbox()

def load_europa():
    global target_graph
    target_graph = build_from_airspace(NAV_EU, SEG_EU, AER_EU)
    draw_graph(target_graph)
    update_airport_listbox()

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
    draw_graph(target_graph)
    update_airport_listbox()

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

# Añadir / borrar nodos y segmentos

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
    
    draw_graph(target_graph, last_path)

def del_node():
    global selected_nodes
    if not target_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    if not selected_nodes:
        messagebox.showinfo("Selecciona", "Selecciona un nodo en el gráfico para borrar.")
        return
    nm = selected_nodes[0]
    # eliminar segmentos asociados
    target_graph.lsegments = [
        s for s in target_graph.lsegments
        if s.origin.name != nm and s.destination.name != nm
    ]
    target_graph.lnodes = [n for n in target_graph.lnodes if n.name != nm]
    selected_nodes.clear()
    draw_graph(target_graph)

def toggle_segments():
    global show_segments
    show_segments = not show_segments
    draw_graph(target_graph) # variable de añadir last path

def add_segment():
    global selected_nodes
    if not target_graph or len(target_graph.lnodes) < 2:
        messagebox.showinfo("Error", "Grafo inaccesible o sin nodos suficientes")
        return
    if len(selected_nodes) < 2:
        messagebox.showinfo("Selecciona", "Selecciona dos nodos (origen y destino) en el gráfico para añadir el segmento.")
        return
    origin, dest = selected_nodes[:2]
    name = f"{origin}-{dest}"
    if not AddSegment(target_graph, name, origin, dest):
        messagebox.showwarning("Aviso", "Segmento no añadido")
    selected_nodes.clear()
    draw_graph(target_graph, last_path)

def del_segment():
    global selected_nodes
    if not target_graph:
        return
    if len(selected_nodes) < 2:
        messagebox.showinfo("Selecciona", "Selecciona dos nodos (origen y destino) en el gráfico para borrar el segmento.")
        return
    origin, dest = selected_nodes[:2]
    name = f"{origin}-{dest}"
    before = len(target_graph.lsegments)
    target_graph.lsegments = [s for s in target_graph.lsegments if s.name != name]
    if len(target_graph.lsegments) == before:
        messagebox.showinfo("Aviso", "Segmento no encontrado")
    selected_nodes.clear()
    draw_graph(target_graph, last_path)

def show_neighbors():
    global selected_nodes
    if not target_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    if not selected_nodes:
        messagebox.showinfo("Selecciona", "Selecciona un nodo en el gráfico para ver sus vecinos.")
        return
    name = selected_nodes[0]
    draw_graph(target_graph, highlight_node=name)
    selected_nodes.clear()

def show_reachable():
    global selected_nodes
    if not target_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    if not selected_nodes:
        messagebox.showinfo("Selecciona", "Selecciona un nodo en el gráfico.")
        return
    start = selected_nodes[0]
    r = ExplorePaths(target_graph, start)
    if r:
        draw_graph(target_graph, pths=r)
    else:
        messagebox.showinfo("Error", "Nodo no válido.")
    selected_nodes.clear()

def shortest_path():
    global target_graph, last_path, cost_label
    if not target_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        if cost_label:
            cost_label.config(text="Coste: -")
        return

    start = simpledialog.askstring("Ruta más corta", "Nodo o aeropuerto origen:")
    if not start:
        if cost_label:
            cost_label.config(text="Coste: -")
        return
    end = simpledialog.askstring("Ruta más corta", "Nodo o aeropuerto destino:")
    if not end:
        if cost_label:
            cost_label.config(text="Coste: -")
        return

    # Si el grafo tiene airspace, permite IDs de aeropuerto
    if hasattr(target_graph, "_airspace"):
        airspace = target_graph._airspace
        # Si es aeropuerto, usar SIDs/STARs, si no, usar el ID directamente
        if start in airspace.airports:
            start_points = airspace.airports[start].sids or airspace.airports[start].stars
        else:
            start_points = [start]
        if end in airspace.airports:
            end_points = airspace.airports[end].stars or airspace.airports[end].sids
        else:
            end_points = [end]
        best_path = None
        best_cost = float('inf')
        for s in start_points:
            for e in end_points:
                path = findShortestPath(target_graph, s, e)
                if path and hasattr(path, 'cost') and path.cost < best_cost:
                    best_path = path
                    best_cost = path.cost
        path = best_path
    else:
        path = findShortestPath(target_graph, start, end)

    if path:
        last_path = path
        draw_graph(target_graph, pth=path)
        if cost_label:
            cost_label.config(text=f"Coste: {path.cost:.2f}")
    else:
        messagebox.showinfo("Error", "No hay ruta.")
        if cost_label:
            cost_label.config(text="Coste: -")

def toggle_map_bg():
    global show_map_bg
    show_map_bg = not show_map_bg
    draw_graph(target_graph, last_path)

def clear_selection():
    global selected_nodes
    selected_nodes.clear()
    draw_graph(target_graph, last_path)

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

def update_airport_listbox():
    airport_listbox.delete(0, tk.END)
    airport_listbox.insert(tk.END, "Aeropuertos:")
    if hasattr(target_graph, "_airspace") and hasattr(target_graph._airspace, "airports"):
        for aid in target_graph._airspace.airports.keys():
            airport_listbox.insert(tk.END, aid)

# Estadísticas del grafo

def show_stats():
    if not target_graph or not hasattr(target_graph, "lnodes") or not hasattr(target_graph, "lsegments"):
        messagebox.showinfo("Estadísticas", "No hay grafo cargado.")
        return
    num_nodes = len(target_graph.lnodes)
    num_segments = len(target_graph.lsegments)
    if num_nodes == 0:
        messagebox.showinfo("Estadísticas", "El grafo está vacío.")
        return
    # Nodo más conectado
    max_deg = -1
    max_node = None
    for n in target_graph.lnodes:
        deg = len(getattr(n, "nl", []))
        if deg > max_deg:
            max_deg = deg
            max_node = n.name
    msg = (
        f"Número de nodos: {num_nodes}\n"
        f"Número de segmentos: {num_segments}\n"
        f"Nodo más conectado: {max_node} ({max_deg} conexiones)\n"
    )
    messagebox.showinfo("Estadísticas del grafo", msg)

# Abrir la vista actual en Google Earth

def open_google_earth():
    global target_graph, last_draw_type, last_draw_data
    if not target_graph:
        messagebox.showwarning("Error", "No hay grafo cargado.")
        return
    out = os.path.join(BASE_DIR, "view.kml")
    try:
        if last_draw_type in ("path", "paths", "highlight") and last_draw_data:
            path_to_kml(target_graph, last_draw_data, out)
        else:
            graph_to_kml(target_graph, out)
        if sys.platform.startswith("win"):
            os.startfile(out)
        elif sys.platform == "darwin":
            subprocess.call(["open", out])
        else:
            subprocess.call(["xdg-open", out])
    except Exception:
        messagebox.showerror("Error", "No se pudo abrir Google Earth.")

# Función para mostrar Funciones extras
def show_new_features():
    novedades = (
        "Novedades recientes:\n"
        "- Interacción con el grafo (pulsar rueda y click izquierdo para moverse)\n"
        "- Boton de enseñar y ocultar segmentos\n"
        "- Boton de estadísticas del grafo\n"
        "- Botón mapa base de cataluña\n"
        "- ¿Qué hay abajo del todo?"

    )
    messagebox.showinfo("Nuevas funcionalidades", novedades)

def show_group_photo():
    img_path = os.path.join(BASE_DIR, "foto_grupal.jpg")  
    if not os.path.exists(img_path):
        messagebox.showinfo("Foto grupal", "No se ha encontrado la foto grupal en la carpeta del proyecto.")
        return
    try:
        img = Image.open(img_path)
        img.thumbnail((400, 400))
        win = tk.Toplevel(root)
        win.title("Foto grupal")
        tk_img = ImageTk.PhotoImage(img)
        label = tk.Label(win, image=tk_img)
        label.image = tk_img  # Mantener referencia
        label.pack()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{e}")

def show_help():
    messagebox.showinfo("¡Sorpresa!", "¡¡¡Miguel y Rubén, sois unos cracks!!!")

# ------------ Interfase Setup ----------------

root = tk.Tk()
root.title("Airspace Explorer v4")
root.geometry("1250x700")

# Frames
ctrl = tk.Frame(root, width=300)
ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
graph_frame = tk.Frame(root)
graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


# Botonera (contenedor de botones y paneles de control)
buttons = tk.LabelFrame(ctrl, text="Control")
buttons.pack(fill=tk.BOTH, expand=True)

# --- Carga de grafos ---
loadGraphFrame = tk.LabelFrame(buttons, text="Load graphs")
loadGraphFrame.grid(row=0, column=0, sticky="nswe", pady=3)
tk.Button(loadGraphFrame, text="Carga Cataluña", command=load_catalunya).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
tk.Button(loadGraphFrame, text="Carga España", command=load_espana).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
tk.Button(loadGraphFrame, text="Carga Europa", command=load_europa).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
tk.Button(loadGraphFrame, text="Carga Archivo", command=load_from_file).grid(row=1, column=1, padx=2, pady=2, sticky="ew")
tk.Button(loadGraphFrame, text="Design Graph", command=design_graph).grid(row=2, column=0, padx=2, pady=2, sticky="ew")
tk.Button(loadGraphFrame, text="Show Example Graph", command=load_example_graph).grid(row=2, column=1, padx=2, pady=2, sticky="ew")
tk.Button(loadGraphFrame, text="Guardar grafo", command=save_to_file).grid(row=3, column=0, columnspan=2, padx=2, pady=2, sticky="ew")
# Lista de aeropuertos
airport_listbox = tk.Listbox(loadGraphFrame, height=4)
airport_listbox.grid(row=4, column=0, columnspan=2, sticky="we", padx=2, pady=2)
airport_listbox.insert(tk.END, "Aeropuertos:")
loadGraphFrame.columnconfigure(0, weight=1)
loadGraphFrame.columnconfigure(1, weight=1)

# --- Operaciones sobre el grafo ---
graphOpsFrame = tk.LabelFrame(buttons, text="Operations")
graphOpsFrame.grid(row=1, column=0, sticky="nswe", pady=3)
tk.Button(graphOpsFrame, text="Add Node", command=add_node).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
tk.Button(graphOpsFrame, text="Delete Node", command=del_node).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
tk.Button(graphOpsFrame, text="Add segment", command=add_segment).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
tk.Button(graphOpsFrame, text="Delete segment", command=del_segment).grid(row=1, column=1, padx=2, pady=2, sticky="ew")
tk.Button(graphOpsFrame, text="CAT_Base map", command=toggle_map_bg).grid(row=2, column=0, padx=2, pady=2, sticky="ew")
tk.Button(graphOpsFrame, text="On/Off segments", command=toggle_segments).grid(row=2, column=1, padx=2, pady=2, sticky="ew")
graphOpsFrame.columnconfigure(0, weight=1)
graphOpsFrame.columnconfigure(1, weight=1)

# --- Consultas ---
queryFrame = tk.LabelFrame(buttons, text="Study")
queryFrame.grid(row=2, column=0, sticky="nswe", pady=3)
tk.Button(queryFrame, text="Neightbors", command=show_neighbors).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
tk.Button(queryFrame, text="Reachable", command=show_reachable).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
tk.Button(queryFrame, text="Shortest Path", command=shortest_path).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
cost_label = tk.Label(queryFrame, text="Cost: -", width=15, anchor="w")
cost_label.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
tk.Button(queryFrame, text="Clear selection", command=clear_selection).grid(row=2, column=0, columnspan=2, padx=2, pady=2, sticky="ew")
queryFrame.columnconfigure(0, weight=1)
queryFrame.columnconfigure(1, weight=1)

# --- Botones de extras ---
extrasFrame = tk.LabelFrame(ctrl, text="Extras")
extrasFrame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
tk.Button(extrasFrame, text="Graph Stats", command=show_stats).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
tk.Button(extrasFrame, text="Extras list", command=show_new_features, fg="blue").grid(row=0, column=1, padx=2, pady=2, sticky="ew")
tk.Button(extrasFrame, text="El team", command=show_group_photo).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
tk.Button(extrasFrame, text="Clica aquí si eres un máquina", command=show_help).grid(row=1, column=1, padx=2, pady=2, sticky="ew")
extrasFrame.columnconfigure(0, weight=1)
extrasFrame.columnconfigure(1, weight=1)

# --- Botones KML ---
kmlFrame = tk.LabelFrame(ctrl, text="Exportar KML")
kmlFrame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
tk.Button(kmlFrame, text="KML Cataluña", command=lambda: export_kml("CAT")).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
tk.Button(kmlFrame, text="KML España",   command=lambda: export_kml("ESP")).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
tk.Button(kmlFrame, text="KML Europa",   command=lambda: export_kml("EUR")).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
tk.Button(kmlFrame, text="Open in Google Earth", command=open_google_earth).grid(row=1, column=1, padx=2, pady=2, sticky="ew")
kmlFrame.columnconfigure(0, weight=1)
kmlFrame.columnconfigure(1, weight=1)

# Arranca la aplicación
root.mainloop()


