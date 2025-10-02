"""
Graph Builder Module

This module provides functions for building various graph representations
from Verilog AST, including CDFGs and dependency graphs.
"""

import networkx as nx
import pprint as pp

from .utils import Type, generate_code, get_root_node, traverse_CDFG


def construct_CDFG(ast, CDFGS, MODINSTS, clks, indent):
    """
    Construct Control/Data Flow Graph from AST.
    
    Args:
        ast: Abstract Syntax Tree node
        CDFGS: List to accumulate CDFGs
        MODINSTS: List for module instantiations
        clks: Clock signals
        indent: Current indentation level
        
    Returns:
        tuple: (CDFGS, MODINSTS) updated lists
    """
    if ast is None:
        return CDFGS, MODINSTS
    
    typ = ast.__class__.__name__
    
    # Handle different AST node types
    if typ == 'Always':
        CDFG = nx.DiGraph()
        add_nodes_to_CDFG(ast, CDFG)
        CDFGS.append(CDFG)
        
    elif typ == 'Initial':
        CDFG = nx.DiGraph()
        add_nodes_to_CDFG(ast, CDFG)
        CDFGS.append(CDFG)
        
    elif typ == 'InstanceList':
        # Handle module instantiations
        for instance in ast.instances:
            MODINSTS.append(instance)
            
    # Recursively process children
    for child in ast.children():
        construct_CDFG(child, CDFGS, MODINSTS, clks, indent + 1)
    
    return CDFGS, MODINSTS


def add_nodes_to_CDFG(ast, CDFG):
    """
    Add nodes to CDFG recursively.
    
    Args:
        ast: Abstract Syntax Tree node
        CDFG: Control/Data Flow Graph to populate
        
    Returns:
        NetworkX DiGraph: Updated CDFG
    """
    if ast is None:
        return CDFG
    
    typ = ast.__class__.__name__
    node_label = Type.get(typ, typ)
    
    # Add current node
    if typ in Type:
        CDFG.add_node(str(id(ast)), label=node_label, typ=typ, ast=ast)
    
    # Add edges to children
    for child in ast.children():
        if child is not None:
            child_typ = child.__class__.__name__
            if child_typ in Type:
                CDFG.add_edge(str(id(ast)), str(id(child)))
                add_nodes_to_CDFG(child, CDFG)
    
    return CDFG


def get_var_def_chain(CDFGS, PathSets, Params):
    """
    Get variable definition chains from CDFGs.
    
    Args:
        CDFGS: List of CDFGs
        PathSets: List of path sets
        Params: Parameter definitions
        
    Returns:
        dict: Variable definition chain mapping
    """
    var_def_chain = {}
    
    for idx, cdfg in enumerate(CDFGS):
        paths = PathSets[idx]
        
        for path in paths:
            # Process each path to extract variable definitions
            for node_id in path:
                if node_id in cdfg.nodes():
                    node_data = cdfg.nodes[node_id]
                    ast_node = node_data.get('ast')
                    
                    if ast_node is not None:
                        # Extract variable definitions from this node
                        process_def_node(ast_node, var_def_chain)
    
    return var_def_chain


def process_def_node(ast_node, var_def_chain):
    """
    Process AST node to extract variable definitions.
    
    Args:
        ast_node: AST node to process
        var_def_chain: Dictionary to update with definitions
    """
    typ = ast_node.__class__.__name__
    
    if typ in ['NonblockingSubstitution', 'BlockingSubstitution', 'Assign']:
        # Extract left-hand side variable
        if hasattr(ast_node, 'left'):
            var_name = get_variable_name(ast_node.left)
            
            if var_name not in var_def_chain:
                var_def_chain[var_name] = {
                    'DDeps': [],
                    'CDeps': [],
                    'Expressions': [],
                    'DLines': [],
                    'CLines': [],
                    'Clocked': False
                }
            
            # Extract right-hand side dependencies
            if hasattr(ast_node, 'right'):
                deps = extract_dependencies(ast_node.right)
                var_def_chain[var_name]['DDeps'].append(deps)
                var_def_chain[var_name]['Expressions'].append(ast_node)


def get_variable_name(ast_node):
    """
    Extract variable name from AST node.
    
    Args:
        ast_node: AST node representing a variable
        
    Returns:
        str: Variable name
    """
    if ast_node is None:
        return ''
    
    typ = ast_node.__class__.__name__
    
    if typ == 'Identifier':
        return ast_node.name
    elif typ == 'Pointer':
        return get_variable_name(ast_node.var)
    else:
        return str(id(ast_node))


def extract_dependencies(ast_node):
    """
    Extract variable dependencies from an expression.
    
    Args:
        ast_node: AST node representing an expression
        
    Returns:
        list: List of dependent variables
    """
    deps = []
    
    if ast_node is None:
        return deps
    
    typ = ast_node.__class__.__name__
    
    if typ == 'Identifier':
        deps.append(ast_node.name)
    elif hasattr(ast_node, 'children'):
        for child in ast_node.children():
            deps.extend(extract_dependencies(child))
    
    return deps


def get_var_use_chain(CDFGS, PathSets, Params):
    """
    Get variable use chains from CDFGs.
    
    Args:
        CDFGS: List of CDFGs
        PathSets: List of path sets
        Params: Parameter definitions
        
    Returns:
        dict: Variable use chain mapping
    """
    var_use_chain = {}
    
    for idx, cdfg in enumerate(CDFGS):
        paths = PathSets[idx]
        
        for path in paths:
            # Process each path to extract variable uses
            for node_id in path:
                if node_id in cdfg.nodes():
                    node_data = cdfg.nodes[node_id]
                    ast_node = node_data.get('ast')
                    
                    if ast_node is not None:
                        # Extract variable uses from this node
                        process_use_node(ast_node, var_use_chain)
    
    return var_use_chain


def process_use_node(ast_node, var_use_chain):
    """
    Process AST node to extract variable uses.
    
    Args:
        ast_node: AST node to process
        var_use_chain: Dictionary to update with uses
    """
    typ = ast_node.__class__.__name__
    
    if typ in ['NonblockingSubstitution', 'BlockingSubstitution', 'Assign']:
        # Extract right-hand side variable uses
        if hasattr(ast_node, 'right'):
            uses = extract_dependencies(ast_node.right)
            
            for var_name in uses:
                if var_name not in var_use_chain:
                    var_use_chain[var_name] = []
                
                # Add this use location
                if hasattr(ast_node, 'left'):
                    lhs = get_variable_name(ast_node.left)
                    var_use_chain[var_name].append(lhs)


def construct_var_dep_graph(var_def_chain, var_use_chain):
    """
    Construct variable dependency graph from def and use chains.
    
    Args:
        var_def_chain: Variable definition chain
        var_use_chain: Variable use chain
        
    Returns:
        NetworkX DiGraph: Variable dependency graph
    """
    dep_g = nx.DiGraph()
    
    # Add edges based on def-use relationships
    for var_name, def_info in var_def_chain.items():
        dep_g.add_node(var_name)
        
        # Add edges to dependencies
        for deps_list in def_info['DDeps']:
            for dep in deps_list:
                if dep and dep != var_name:
                    dep_g.add_edge(dep, var_name, weight=1)
    
    return dep_g


def build_cdfg(ast, clocks, params, ports):
    """
    Main function to build CDFG from AST.
    
    Args:
        ast: Abstract Syntax Tree
        clocks: List of clock signals
        params: Parameter definitions
        ports: Port definitions
        
    Returns:
        dict: Dictionary containing all CDFG information
    """
    CDFGS = []
    MODINSTS = []
    
    # Construct CDFGs
    CDFGS, MODINSTS = construct_CDFG(ast, CDFGS, MODINSTS, clocks, 0)
    
    # Build path sets
    PathSets = []
    for cdfg in CDFGS:
        if len(cdfg.nodes()) > 0:
            paths = traverse_CDFG(cdfg)
            PathSets.append(paths)
        else:
            PathSets.append([])
    
    # Build def and use chains
    var_def_chain = get_var_def_chain(CDFGS, PathSets, params)
    var_use_chain = get_var_use_chain(CDFGS, PathSets, params)
    
    # Build dependency graph
    dep_g = construct_var_dep_graph(var_def_chain, var_use_chain)
    
    return {
        'CDFGS': CDFGS,
        'PathSets': PathSets,
        'var_def_chain': var_def_chain,
        'var_use_chain': var_use_chain,
        'dep_g': dep_g,
        'MODINSTS': MODINSTS
    }
