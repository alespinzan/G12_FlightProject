import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from graph import *
from node import *
from test_graph import G

# Global graph object
current_graph = None

def load_example_graph():
    global current_graph
    current_graph = G 
    Plot(G)
    update_node_list()

def load_invented_graph():
    global current_graph
    current_graph = Graph()
    # Your own graph example
    AddNode(current_graph, node("X", 1, 1))
    AddNode(current_graph, node("Y", 3, 4))
    AddNode(current_graph, node("Z", 5, 2))
    AddSegment(current_graph, "X-Y", "X", "Y")
    AddSegment(current_graph, "Y-Z", "Y", "Z")
    Plot(current_graph)
    update_node_list()

def load_graph_from_file():
    global current_graph
    filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if filepath:
        current_graph = readfile(filepath)
        Plot(current_graph)
        update_node_list()

def show_neighbors():
    global current_graph
    selected = listbox_nodes.curselection()
    if not current_graph or not selected:
        messagebox.showinfo("Select a node", "Please select a node to display its neighbors.")
        return
    name = listbox_nodes.get(selected[0])
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
        messagebox.showinfo("Error", "No graph loaded. Please load or create a graph first.")
        return
    name = simpledialog.askstring("Add Node", "Enter node name:")
    x = simpledialog.askfloat("Add Node", "Enter x-coordinate:")
    y = simpledialog.askfloat("Add Node", "Enter y-coordinate:")
    if name and x is not None and y is not None:
        AddNode(current_graph, node(name, x, y))
        Plot(current_graph)
        update_node_list()

def add_segment():
    global current_graph
    if not current_graph:
        messagebox.showinfo("Error", "No graph loaded. Please load or create a graph first.")
        return
    origin = simpledialog.askstring("Add Segment", "Enter origin node name:")
    destination = simpledialog.askstring("Add Segment", "Enter destination node name:")
    if origin and destination:
        segment_name = f"{origin}-{destination}"
        AddSegment(current_graph, segment_name, origin, destination)
        Plot(current_graph)

def delete_node():
    global current_graph
    if not current_graph:
        messagebox.showinfo("Error", "No graph loaded. Please load or create a graph first.")
        return
    name = simpledialog.askstring("Delete Node", "Enter node name to delete:")
    if name:
        if deleteNode(current_graph, name):  
            update_node_list()
        else:
            messagebox.showinfo("Error", f"Node '{name}' not found.")

def design_graph():
    global current_graph
    current_graph = Graph()
    update_node_list()

def save_graph_to_file():
    global current_graph
    if not current_graph:
        messagebox.showinfo("Error", "No graph loaded. Please load or create a graph first.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if filepath:
        save_graph_to_file(current_graph, filepath)
        messagebox.showinfo("Success", f"Graph saved to {filepath}")

def load_current_graph():
    global current_graph
    return Plot(current_graph)

def find_shotest_path():
    global current_graph
    if not current_graph:
        messagebox.showinfo("Error", "No graph loaded. Please load or create a graph first.")
        return
    start_node = simpledialog.askstring("Shortest Path", "Enter start node name:")
    end_node = simpledialog.askstring("Shortest Path", "Enter end node name:")
    
    if start_node and end_node:
        path = findShortestPath(current_graph, start_node, end_node)
        if path:
            PlotPath(current_graph, path)
        else:
            messagebox.showinfo("Error", f"No path found from '{start_node}' to '{end_node}'.")

def show_reachable_nodes():
    global current_graph
    if not current_graph:
        messagebox.showinfo("Error", "No graph loaded. Please load or create a graph first.")
        return
    start_node = simpledialog.askstring("Reachable Nodes", "Enter start node name:")
    if start_node:
        reachable_nodes = ExplorePaths(current_graph, start_node)
        if reachable_nodes:
            PlotPaths(current_graph, reachable_nodes)
        else:
            messagebox.showinfo("Error, node not in graph")

# --- GUI SETUP ---

root = tk.Tk()
root.geometry("900x500")
root.title("Airways Visualizer")

# Root layout
root.columnconfigure(index=0, weight=1)
root.columnconfigure(index=1, weight=10)
root.rowconfigure(index=0, weight=1)
root.rowconfigure(index=1, weight=1)
root.rowconfigure(index=2, weight=1)

# LoadGraphFrame set up:
loadGraphFrame = tk.LabelFrame(root, text = "Load Graphs")
loadGraphFrame.grid(row=0, column=0,padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)
loadGraphFrame.rowconfigure(index=0, weight=1)
loadGraphFrame.rowconfigure(index=1, weight=1)
loadGraphFrame.columnconfigure(index=0, weight=1)
loadGraphFrame.columnconfigure(index=1, weight=1)

btn1 = tk.Button(loadGraphFrame, text="Show Example Graph", command=load_example_graph)
btn1.grid(row=0, column=0, padx=1, pady=1)

btn2 = tk.Button(loadGraphFrame, text="Load Graph from File", command=load_graph_from_file)
btn2.grid(row=0, column=1, padx=1, pady=1)

btn3 = tk.Button(loadGraphFrame, text="Design Graph", command=design_graph)
btn3.grid(row=1, column=0, padx=1, pady=1)

btn4 = tk.Button(loadGraphFrame, text="Save Graph to File", command=save_graph_to_file)
btn4.grid(row=1, column=1, padx=1, pady=1)

# current graph SetUP
currentGraph = tk.LabelFrame(root, text = "Current Graph")
currentGraph.grid(row=1, column=0,padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)
currentGraph.rowconfigure(index=0, weight=1)
currentGraph.rowconfigure(index=1, weight=1)
currentGraph.columnconfigure(index=0, weight=1)
currentGraph.columnconfigure(index=1, weight=1)
currentGraph.columnconfigure(index=2, weight=4)

btn5 = tk.Button(currentGraph, text="Add Node", command=add_node)
btn5.grid(row=0, column=0, padx=1, pady=1)

btn6 = tk.Button(currentGraph, text="Add Segment", command=add_segment)
btn6.grid(row=0, column=1, padx=1, pady=1)

btn7 = tk.Button(currentGraph, text="Delete Node", command=delete_node)
btn7.grid(row=1, column=0, padx=1, pady=1)

btn8 = tk.Button(currentGraph, text="Show current Graph", command=load_current_graph)
btn8.grid(row=0, column=2, padx=1, pady=1)

frame_nodes = tk.Frame(currentGraph)
frame_nodes.grid(row=1, column=2, columnspan=1, padx=1, pady=1, sticky=tk.N + tk.E + tk.W + tk.S)

listbox_nodes = tk.Listbox(frame_nodes, height=5, width=15)
listbox_nodes.pack()

btn9 = tk.Button(currentGraph, text="Show Neighbors", command=show_neighbors)
btn9.grid(row=1, column=1, padx=1, pady=1)

# Rute
ruteSetup = tk.LabelFrame(root, text = "Rute Setup")
ruteSetup.grid(row=2, column=0,padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)
ruteSetup.rowconfigure(index=0, weight=1)
ruteSetup.columnconfigure(index=0, weight=1)
ruteSetup.columnconfigure(index=1, weight=1)

btn10 = tk.Button(ruteSetup, text="Find Shortest Path", command=find_shotest_path)
btn10.grid(row=0, column=0, padx=1, pady=1)

btn11 = tk.Button(ruteSetup, text="Show Reachable Nodes", command=show_reachable_nodes)
btn11.grid(row=0, column=1, padx=1, pady=1)

# Graph Frame

graphFrame = tk.LabelFrame(root, text = "Graph")
ruteSetup.grid(row=0, column=1,padx=5, pady=5, sticky=tk.N + tk.E + tk.W + tk.S)

root.mainloop()