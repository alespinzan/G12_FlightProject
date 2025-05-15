import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from graph import *
from node import *
from test_graph import G
from airspace import *

# Rutas por defecto (ajusta si tienen extensión .txt u otra)
BASE_DIR = os.path.dirname(__file__)
NAV_FILE = os.path.join(BASE_DIR, "Cat_nav")
SEG_FILE = os.path.join(BASE_DIR, "Cat_seg")
AER_FILE = os.path.join(BASE_DIR, "Cat_aer")

# Globales para canvas y grafo actual
current_graph = None
graph_canvas  = None

def draw_graph(g, pth=None, pths=None):
    global graph_canvas
    # Limpia lo anterior
    for w in graphFrame.winfo_children():
        w.destroy()

    fig = Figure(figsize=(5,5))
    ax  = fig.add_subplot(111)
    if pth is not None:
        PlotPath(g, pth, ax)
    elif pths is not None:
        PlotPaths(g, pths, ax)
    else:
        DrawBaseGraph(g, ax)

    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_title("Graph Visualization with Arrows")
    ax.grid(True, linestyle="--", linewidth=0.5, color="red")

    graph_canvas = FigureCanvasTkAgg(fig, master=graphFrame)
    graph_canvas.draw()
    graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
    fig.clear()

def load_example_graph():
    global current_graph
    current_graph = G
    draw_graph(G)
    update_node_list()

def load_graph_from_file():
    global current_graph
    filepath = tk.filedialog.askopenfilename(filetypes=[("Text Files","*.txt")])
    if not filepath:
        return
    current_graph = readfile(filepath)
    draw_graph(current_graph)
    update_node_list()

def show_neighbors():
    global current_graph
    sel = listbox_nodes.curselection()
    if not current_graph or not sel:
        messagebox.showinfo("Select a node", "Selecciona un nodo primero.")
        return
    name = listbox_nodes.get(sel[0])
    PlotNode(current_graph, name)

def update_node_list():
    if not current_graph:
        return
    listbox_nodes.delete(0, tk.END)
    for n in current_graph.lnodes:
        listbox_nodes.insert(tk.END, n.name)

def add_node():
    global current_graph
    if not current_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    name = simpledialog.askstring("Add Node","Nombre nodo:")
    x = simpledialog.askfloat("Add Node","Coordenada X:")
    y = simpledialog.askfloat("Add Node","Coordenada Y:")
    if name and x is not None and y is not None:
        AddNode(current_graph, node(name,x,y))
        draw_graph(current_graph)
        update_node_list()

def add_segment():
    global current_graph
    if not current_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    o = simpledialog.askstring("Add Segment","Nodo origen:")
    d = simpledialog.askstring("Add Segment","Nodo destino:")
    if o and d:
        name = f"{o}-{d}"
        AddSegment(current_graph,name,o,d)
        draw_graph(current_graph)

def delete_node():
    global current_graph
    if not current_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    name = simpledialog.askstring("Delete Node","Nodo a borrar:")
    if name and deleteNode(current_graph,name):
        update_node_list()
    else:
        messagebox.showinfo("Error", f"'{name}' no existe.")

def design_graph():
    global current_graph
    current_graph = Graph()
    draw_graph(current_graph)
    update_node_list()

def save_graph_to_file():
    global current_graph
    if not current_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    fp = tk.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files","*.txt")])
    if fp:
        save_graph_to_file(current_graph, fp)
        messagebox.showinfo("Guardado", f"Grafo guardado en {fp}")

def find_shotest_path():
    global current_graph
    if not current_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    start = simpledialog.askstring("Shortest Path","Nodo inicio:")
    end   = simpledialog.askstring("Shortest Path","Nodo fin:")
    if start and end:
        path = findShortestPath(current_graph,start,end)
        if path:
            draw_graph(current_graph, pth=path)
        else:
            messagebox.showinfo("Error", "No hay ruta.")

def show_reachable_nodes():
    global current_graph
    if not current_graph:
        messagebox.showinfo("Error", "Carga o crea un grafo primero.")
        return
    start = simpledialog.askstring("Reachable","Nodo inicio:")
    if start:
        r = ExplorePaths(current_graph, start)
        if r:
            draw_graph(current_graph, pths=r)
        else:
            messagebox.showinfo("Error","Nodo no válido.")

# -------------------------------------------------------------------
# Handler global para visualizar el espacio aéreo de Cataluña
# -------------------------------------------------------------------
def visualizar_cataluna():
    global current_graph

    # 1) Carga los datos de Cataluña
    aspace = AirSpace()
    aspace.load_navpoints(NAV_FILE)
    aspace.load_navsegments(SEG_FILE)
    aspace.load_airports(AER_FILE)

    # 2) Construye manualmente un Graph válido
    g = Graph()
    # Añade cada NavPoint como nodo
    for np_obj in aspace.navpoints.values():
        # convierte NavPoint → node para Graph
        AddNode(g, node(np_obj.id, np_obj.latitude, np_obj.longitude))
    # Añade cada NavSegment como arista
    for seg in aspace.navsegments:
        seg_name = f"{seg.origin.id}-{seg.destination.id}"
        AddSegment(g, seg_name, seg.origin.id, seg.destination.id)

    # 3) Actualiza la variable global
    current_graph = g

    # 4) Limpia el frame y dibuja el grafo cargado
    for widget in graphFrame.winfo_children():
        widget.destroy()
    draw_graph(current_graph)

    # 5) Refresca la lista de nodos para los handlers de vecinos/A*/alcance
    update_node_list()


# -------------------------------------------------------------------
# Construcción de la interfaz
# -------------------------------------------------------------------
root = tk.Tk()
root.geometry("1000x500")
root.title("Airways Visualizer")

# Divide en dos columnas: botones | gráfico
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=4)
root.rowconfigure(0, weight=1)

# Frame de botones a la izquierda
buttons = tk.Frame(root)
buttons.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)

# Frame de gráfica a la derecha
graphFrame = tk.LabelFrame(root, text="Graph")
graphFrame.grid(row=0, column=1, sticky="nswe", padx=5, pady=5)

# --- Load Graphs ---
loadGraphFrame = tk.LabelFrame(buttons, text="Load Graphs")
loadGraphFrame.grid(row=0, column=0, sticky="we", pady=3)
btn1 = tk.Button(loadGraphFrame, text="Show Example Graph", command=load_example_graph)
btn2 = tk.Button(loadGraphFrame, text="Load Graph from File", command=load_graph_from_file)
btn3 = tk.Button(loadGraphFrame, text="Design Graph", command=design_graph)
btn4 = tk.Button(loadGraphFrame, text="Save Graph to File", command=save_graph_to_file)
btn1.grid(row=0,column=0,padx=2,pady=2); btn2.grid(row=0,column=1,padx=2,pady=2)
btn3.grid(row=1,column=0,padx=2,pady=2); btn4.grid(row=1,column=1,padx=2,pady=2)

# --- Current Graph ---
currentGraph = tk.LabelFrame(buttons, text="Current Graph")
currentGraph.grid(row=1, column=0, sticky="we", pady=3)
btn5 = tk.Button(currentGraph, text="Add Node", command=add_node)
btn6 = tk.Button(currentGraph, text="Add Segment", command=add_segment)
btn7 = tk.Button(currentGraph, text="Delete Node", command=delete_node)
btn8 = tk.Button(currentGraph, text="Show current Graph", command=lambda: draw_graph(current_graph))
btn9 = tk.Button(currentGraph, text="Show Neighbors", command=show_neighbors)
frame_nodes = tk.Frame(currentGraph)
listbox_nodes = tk.Listbox(frame_nodes, height=5, width=15)
frame_nodes.grid(row=1,column=2); listbox_nodes.pack()
btn5.grid(row=0,column=0,padx=2,pady=2); btn6.grid(row=0,column=1,padx=2,pady=2)
btn7.grid(row=1,column=0,padx=2,pady=2); btn8.grid(row=0,column=2,padx=2,pady=2)
btn9.grid(row=1,column=1,padx=2,pady=2)

# --- Rute Setup ---
ruteSetup = tk.LabelFrame(buttons, text="Rute Setup")
ruteSetup.grid(row=2, column=0, sticky="we", pady=3)
btn10 = tk.Button(ruteSetup, text="Find Shortest Path",    command=find_shotest_path)
btn11 = tk.Button(ruteSetup, text="Show Reachable Nodes",  command=show_reachable_nodes)
btn10.grid(row=0,column=0,padx=2,pady=2); btn11.grid(row=0,column=1,padx=2,pady=2)

# --- Espacio Aéreo Cataluña ---
catalunaFrame = tk.LabelFrame(buttons, text="Espacio Aéreo Cataluña")
catalunaFrame.grid(row=3, column=0, sticky="we", pady=3)
btn_vis_cat = tk.Button(catalunaFrame, text="Visualizar Cataluña", command=visualizar_cataluna)
btn_vis_cat.pack(padx=2, pady=2)

root.mainloop()
