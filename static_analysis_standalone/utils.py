"""
Utility Functions for Static Analysis

This module provides utility functions used across the static analysis standalone module.
"""

import networkx as nx
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator


# Node Type Dictionary for Graphs
Type = {
    'IfStatement': 'IF',
    'CaseStatement': 'CS',
    'CasexStatement': 'CX',
    'Case': 'CA',
    'Block': 'BL',
    'NonblockingSubstitution': 'NS',
    'BlockingSubstitution': 'BS',
    'Assign': 'AS',
    'Always': 'AL',
    'SingleStatement': 'SS',
    'EventStatement': 'ES'
}

# Fill Colors for Graph Visualization
FillColor = {
    'IfStatement': 'springgreen',
    'CaseStatement': 'linen',
    'CasexStatement': 'lightgray',
    'Case': 'lightcyan',
    'Block': 'turquoise',
    'NonblockingSubstitution': 'firebrick',
    'BlockingSubstitution': 'cadetblue',
    'Assign': 'deepskyblue',
    'Always': 'gold',
    'SingleStatement': 'aquamarine',
    'EventStatement': 'azure',
    'Default': 'white'
}


def generate_code(ast):
    """
    Generate Verilog code from AST.
    
    Args:
        ast: Abstract Syntax Tree node
        
    Returns:
        str: Generated Verilog code
    """
    codegen = ASTCodeGenerator()
    code = codegen.visit(ast)
    return code


def fill_color(typ):
    """
    Get fill color for a node type.
    
    Args:
        typ: Node type string
        
    Returns:
        str: Color name for visualization
    """
    try:
        return FillColor[typ]
    except KeyError:
        return FillColor['Default']


def get_root_node(graph):
    """
    Get root node(s) of a directed graph.
    
    Args:
        graph: NetworkX DiGraph
        
    Returns:
        list: List of root nodes (nodes with no predecessors)
    """
    return [node for node in graph.nodes() if graph.in_degree(node) == 0]


def get_leaf_nodes(graph):
    """
    Get leaf node(s) of a directed graph.
    
    Args:
        graph: NetworkX DiGraph
        
    Returns:
        list: List of leaf nodes (nodes with no successors)
    """
    return [node for node in graph.nodes() if graph.out_degree(node) == 0]


def all_unique_paths(graph, src, dst):
    """
    Find all unique paths between source and destination in a graph.
    
    Args:
        graph: NetworkX DiGraph
        src: Source node
        dst: Destination node
        
    Returns:
        list: List of all unique paths
    """
    paths = []
    nodes = list(graph.nodes())
    visited = [False] * len(nodes)
    path = []
    
    all_unique_path_dfs(graph, nodes, src, dst, visited, path, paths)
    
    return paths


def all_unique_path_dfs(graph, nodes, u, d, visited, path, paths):
    """
    DFS helper function for finding all unique paths.
    
    Args:
        graph: NetworkX DiGraph
        nodes: List of all nodes
        u: Current node
        d: Destination node
        visited: List tracking visited nodes
        path: Current path being explored
        paths: List to accumulate all paths
    """
    idx = nodes.index(u)
    visited[idx] = True
    path.append(u)
    
    if u == d:
        paths.append(path[:])
    else:
        for node in graph.successors(u):
            node_idx = nodes.index(node)
            if not visited[node_idx]:
                all_unique_path_dfs(graph, nodes, node, d, visited, path, paths)
    
    path.pop()
    visited[idx] = False


def gvn(v, idx):
    """
    Generate variable name from variable components.
    
    Args:
        v: Variable components (list)
        idx: Index mode (0 or 1)
        
    Returns:
        str: Generated variable name
    """
    var_name = ''
    if idx == 0:
        var_name = v[0] + '.'.join(filter(None, v[1:]))
    elif idx == 1:
        var_name = '.'.join(filter(None, v[1:]))
    
    return var_name


def find(dep, DDeps):
    """
    Find dependency in data dependency list.
    
    Args:
        dep: Dependency to find
        DDeps: List of data dependencies
        
    Returns:
        tuple: (index, dependency) if found, (None, None) otherwise
    """
    for idx, ddep in enumerate(DDeps):
        if dep in ddep:
            return (idx, ddep)
    
    return (None, None)


def traverse_CDFG(cdfg):
    """
    Traverse CDFG and return all unique paths from root to leaf.
    
    Args:
        cdfg: Control/Data Flow Graph (NetworkX DiGraph)
        
    Returns:
        list: All unique paths from root to leaf node
    """
    root_node = get_root_node(cdfg)[0]
    leaf_node = get_leaf_nodes(cdfg)[0]
    
    unique_paths_in_cdfg = all_unique_paths(cdfg, root_node, leaf_node)
    
    return unique_paths_in_cdfg


def expr_length(comm_expr):
    """
    Calculate the length/complexity of an expression.
    
    Args:
        comm_expr: Common expression string
        
    Returns:
        int: Length of the expression
    """
    return len(comm_expr)
