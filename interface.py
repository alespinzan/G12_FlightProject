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
        if delete_node(current_graph, name):  # Llamada corregida
            Plot(current_graph)
            update_node_list()
        else:
            messagebox.showinfo("Error", f"Node '{name}' not found.")

def design_graph():
    global current_graph
    current_graph = Graph()
    Plot(current_graph)
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

# --- GUI SETUP ---

root = tk.Tk()
root.geometry("600x400")
root.title("Graph Viewer")

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

btn1 = tk.Button(frame_buttons, text="Show Example Graph", command=load_example_graph)
btn1.grid(row=0, column=0, padx=5)

btn2 = tk.Button(frame_buttons, text="Show Invented Graph", command=load_invented_graph)
btn2.grid(row=0, column=1, padx=5)

btn3 = tk.Button(frame_buttons, text="Load Graph from File", command=load_graph_from_file)
btn3.grid(row=0, column=2, padx=5)

btn5 = tk.Button(frame_buttons, text="Add Node", command=add_node)
btn5.grid(row=1, column=0, padx=5)

btn6 = tk.Button(frame_buttons, text="Add Segment", command=add_segment)
btn6.grid(row=1, column=1, padx=5)

btn7 = tk.Button(frame_buttons, text="Delete Node", command=delete_node)
btn7.grid(row=1, column=2, padx=5)

btn8 = tk.Button(frame_buttons, text="Design Graph", command=design_graph)
btn8.grid(row=2, column=0, padx=5)

btn9 = tk.Button(frame_buttons, text="Save Graph to File", command=save_graph_to_file)
btn9.grid(row=2, column=1, padx=5)

btn10 = tk.Button(frame_buttons, text="Show current Graph", command = load_current_graph)
btn10.grid(row=2, column=2, padx=10)

frame_nodes = tk.Frame(root)
frame_nodes.pack(pady=10)

label = tk.Label(frame_nodes, text="Select a node to show neighbors:")
label.pack()

listbox_nodes = tk.Listbox(frame_nodes, height=10, width=30)
listbox_nodes.pack()

btn4 = tk.Button(root, text="Show Neighbors", command=show_neighbors)
btn4.pack(pady=10)

root.mainloop()