"""
Graph Visualizer Module

This module provides functions for visualizing CDFGs and dependency graphs.
"""

import os
import networkx as nx
import pygraphviz as pgv
from .utils import fill_color, get_root_node, generate_code


def plot_digraph(digraphs, curr_path, root):
    """
    Plot and save directed graphs.
    
    Args:
        digraphs: List of directed graphs to plot
        curr_path: Current path for saving outputs
        root: List of root node names for file naming
        
    Returns:
        None
    """
    for idx, digraph in enumerate(digraphs):
        if digraph.number_of_nodes() == 0:
            continue
        
        # Create PyGraphviz graph
        G = pgv.AGraph(directed=True, strict=False)
        
        # Add nodes with attributes
        for node in digraph.nodes():
            node_data = digraph.nodes[node]
            label = node_data.get('label', str(node))
            typ = node_data.get('typ', 'Default')
            color = fill_color(typ)
            
            G.add_node(node, label=label, fillcolor=color, style='filled')
        
        # Add edges
        for edge in digraph.edges():
            src, dst = edge
            edge_data = digraph.edges[edge]
            weight = edge_data.get('weight', 1)
            
            G.add_edge(src, dst, label=str(weight))
        
        # Set graph layout
        G.layout(prog='dot')
        
        # Save as PNG
        if idx < len(root):
            filename = os.path.join(curr_path, root[idx] + '.png')
        else:
            filename = os.path.join(curr_path, f'graph_{idx}.png')
        
        G.draw(filename)
        
        # Also save as DOT file
        dot_filename = filename.replace('.png', '.dot')
        G.write(dot_filename)


def plot_digraphs(CDFGS, cdfg_dir_name):
    """
    Plot multiple CDFGs.
    
    Args:
        CDFGS: List of CDFG graphs
        cdfg_dir_name: Directory name for saving outputs
        
    Returns:
        None
    """
    if not os.path.exists(cdfg_dir_name):
        os.makedirs(cdfg_dir_name)
    
    for idx, cdfg in enumerate(CDFGS):
        if cdfg.number_of_nodes() == 0:
            continue
        
        # Create PyGraphviz graph
        G = pgv.AGraph(directed=True, strict=False)
        
        # Add nodes with attributes
        for node in cdfg.nodes():
            node_data = cdfg.nodes[node]
            label = node_data.get('label', str(node))
            typ = node_data.get('typ', 'Default')
            color = fill_color(typ)
            
            # Add AST code as tooltip if available
            ast_node = node_data.get('ast')
            tooltip = ''
            if ast_node is not None:
                try:
                    tooltip = generate_code(ast_node)
                except:
                    tooltip = str(ast_node)
            
            G.add_node(node, label=label, fillcolor=color, style='filled', 
                      tooltip=tooltip)
        
        # Add edges
        for edge in cdfg.edges():
            src, dst = edge
            G.add_edge(src, dst)
        
        # Set graph layout
        G.layout(prog='dot')
        
        # Save as PNG
        filename = os.path.join(cdfg_dir_name, f'cdfg_{idx}.png')
        G.draw(filename)
        
        # Also save as DOT file
        dot_filename = filename.replace('.png', '.dot')
        G.write(dot_filename)


def save_dependency_graph(dep_g, output_path, filename='dependency_graph'):
    """
    Save dependency graph to file.
    
    Args:
        dep_g: Dependency graph (NetworkX DiGraph)
        output_path: Output directory path
        filename: Base filename for output
        
    Returns:
        None
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # Create PyGraphviz graph
    G = pgv.AGraph(directed=True, strict=False)
    
    # Add nodes
    for node in dep_g.nodes():
        G.add_node(node, label=node, shape='box', style='filled', 
                  fillcolor='lightblue')
    
    # Add edges with weights
    for edge in dep_g.edges(data=True):
        src, dst, data = edge
        weight = data.get('weight', 1)
        G.add_edge(src, dst, label=str(weight))
    
    # Set graph layout
    G.layout(prog='dot')
    
    # Save as PNG
    png_file = os.path.join(output_path, filename + '.png')
    G.draw(png_file)
    
    # Save as DOT
    dot_file = os.path.join(output_path, filename + '.dot')
    G.write(dot_file)
    
    # Also save edge list as text
    txt_file = os.path.join(output_path, filename + '.txt')
    with open(txt_file, 'w') as f:
        f.write("Variable Dependency Graph\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Number of variables: {dep_g.number_of_nodes()}\n")
        f.write(f"Number of dependencies: {dep_g.number_of_edges()}\n\n")
        f.write("Dependencies (from -> to):\n")
        f.write("-" * 50 + "\n")
        
        for edge in dep_g.edges(data=True):
            src, dst, data = edge
            weight = data.get('weight', 1)
            f.write(f"{src} -> {dst} (weight: {weight})\n")


def save_path_information(PathSets, output_path, filename='paths'):
    """
    Save path information to file.
    
    Args:
        PathSets: List of path sets
        output_path: Output directory path
        filename: Base filename for output
        
    Returns:
        None
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    txt_file = os.path.join(output_path, filename + '.txt')
    with open(txt_file, 'w') as f:
        f.write("Path Information\n")
        f.write("=" * 50 + "\n\n")
        
        for idx, paths in enumerate(PathSets):
            f.write(f"CDFG {idx}:\n")
            f.write(f"  Number of paths: {len(paths)}\n")
            
            for path_idx, path in enumerate(paths):
                f.write(f"  Path {path_idx}: {' -> '.join(path)}\n")
            
            f.write("\n")


def visualize_graph(cdfg_info, output_dir='./output'):
    """
    Main function to visualize all graphs from CDFG information.
    
    Args:
        cdfg_info: Dictionary containing CDFG information
        output_dir: Output directory for visualization files
        
    Returns:
        None
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Visualize CDFGs
    cdfg_dir = os.path.join(output_dir, 'cdfgs')
    plot_digraphs(cdfg_info['CDFGS'], cdfg_dir)
    
    # Visualize dependency graph
    dep_dir = os.path.join(output_dir, 'dependency')
    save_dependency_graph(cdfg_info['dep_g'], dep_dir)
    
    # Save path information
    path_dir = os.path.join(output_dir, 'paths')
    save_path_information(cdfg_info['PathSets'], path_dir)
    
    print(f"Visualization complete. Results saved to: {output_dir}")
    print(f"  - CDFGs: {cdfg_dir}")
    print(f"  - Dependency graph: {dep_dir}")
    print(f"  - Path information: {path_dir}")
