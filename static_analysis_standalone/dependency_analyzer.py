"""
Dependency Analyzer Module

This module provides functions for analyzing variable dependencies,
computing cone of influence, and temporal analysis.
"""

import networkx as nx
from .utils import gvn, find, generate_code


def dependencies(var, ELABORATE_INFO, scope_module_map, top_module, dep_g, k, kmax):
    """
    Compute dependencies for a variable at a given temporal depth.
    
    Args:
        var: Variable triplet (cycle, scope, var_name)
        ELABORATE_INFO: Elaborated module information
        scope_module_map: Mapping from scope to module
        top_module: Top-level module name
        dep_g: Dependency graph
        k: Current temporal depth
        kmax: Maximum temporal depth
        
    Returns:
        list: List of dependencies
    """
    deps = []
    
    var_name = gvn(var, 1)
    deps_from_dep_g = list(dep_g.predecessors(var_name))
    
    if not deps_from_dep_g:
        # var is a primary input and has no dependencies
        return deps
    
    scope = var[1]
    module = top_module if not scope else scope_module_map[scope]
    var_def_chain = ELABORATE_INFO[module]['var_def_chain']
    
    try:
        DDeps = var_def_chain[var[2]]['DDeps']
        Clocked = var_def_chain[var[2]]['Clocked']
        Expressions = var_def_chain[var[2]]['Expressions']
    except KeyError:
        # Handling the instantiation connection
        lookback_string = var[0]
        scope = ['' if '.' not in i else i[:i.rfind('.')] for i in deps_from_dep_g]
        var_list = [i if '.' not in i else i[i.rfind('.') + 1:] for i in deps_from_dep_g]
        for j in range(len(scope)):
            deps.append([lookback_string, scope[j], var_list[j]])
        
        return deps
    
    for dep in deps_from_dep_g:
        found = find(dep, DDeps)
        
        # Handling data dependencies
        if found[0] is not None:
            expression = Expressions[found[0]]
            exp_typ = expression.__class__.__name__
            
            if exp_typ == 'NonblockingSubstitution':
                # Non-blocking assignments introduce temporal dependency
                if Clocked:
                    nxt_k = k + 1
                    if nxt_k < kmax:
                        lookback_string = '[' + str(nxt_k) + ']'
                        deps.append([lookback_string,
                                   '' if '.' not in dep else dep[:dep.rfind('.')],
                                   dep if '.' not in dep else dep[dep.rfind('.') + 1:]])
            else:
                lookback_string = '[' + str(k) + ']' if k > 0 else ''
                deps.append([lookback_string,
                           '' if '.' not in dep else dep[:dep.rfind('.')],
                           dep if '.' not in dep else dep[dep.rfind('.') + 1:]])
    
    return deps


def cone_of_influence(vtargets, ELABORATE_INFO, scope_module_map, top_module, 
                      dep_g, temp_length, temp_length_max, PageRank):
    """
    Compute cone of influence for target variables.
    
    Args:
        vtargets: Target variables
        ELABORATE_INFO: Elaborated module information
        scope_module_map: Mapping from scope to module
        top_module: Top-level module name
        dep_g: Dependency graph
        temp_length: Current temporal length
        temp_length_max: Maximum temporal length
        PageRank: PageRank scores for variables
        
    Returns:
        list: Cone of influence information for each target
    """
    cones = []
    
    for vtarget in vtargets:
        cone = temporal_cone(vtarget, temp_length, temp_length_max, vtarget,
                           PageRank, dep_g, ELABORATE_INFO, scope_module_map, 
                           top_module)
        cones.append(cone)
    
    return cones


def temporal_cone(var, temp_length, temp_length_max, vtarget, PageRank, dep_g,
                 ELABORATE_INFO, scope_module_map, top_module):
    """
    Compute temporal cone for a variable.
    
    Args:
        var: Current variable
        temp_length: Current temporal depth
        temp_length_max: Maximum temporal depth
        vtarget: Target variable
        PageRank: PageRank scores
        dep_g: Dependency graph
        ELABORATE_INFO: Elaborated module information
        scope_module_map: Scope to module mapping
        top_module: Top-level module name
        
    Returns:
        dict: Temporal cone information
    """
    cone = {
        'variable': var,
        'depth': temp_length,
        'dependencies': []
    }
    
    if temp_length >= temp_length_max:
        return cone
    
    # Get dependencies at current depth
    deps = dependencies(var, ELABORATE_INFO, scope_module_map, top_module,
                       dep_g, temp_length, temp_length_max)
    
    cone['dependencies'] = deps
    
    # Recursively compute for dependencies
    for dep in deps:
        dep_cone = temporal_cone(dep, temp_length + 1, temp_length_max,
                                vtarget, PageRank, dep_g, ELABORATE_INFO,
                                scope_module_map, top_module)
        cone['dependencies'].append(dep_cone)
    
    return cone


def expressions(var, top_module, scope_module_map, ELABORATE_INFO):
    """
    Get expressions for a variable.
    
    Args:
        var: Variable triplet
        top_module: Top-level module name
        scope_module_map: Scope to module mapping
        ELABORATE_INFO: Elaborated module information
        
    Returns:
        dict: Mapping from line numbers to expressions
    """
    scope = var[1]
    module = top_module if not scope else scope_module_map[scope]
    var_def_chain = ELABORATE_INFO[module]['var_def_chain']
    v = var[2]
    
    X = {}
    try:
        cdeps = var_def_chain[v]['CDeps']
        clines = var_def_chain[v]['CLines']
        expression = var_def_chain[v]['Expressions']
        dlines = var_def_chain[v]['DLines']
    except KeyError:
        return X
    
    # Adding data dependency expressions
    for idx in range(len(expression)):
        expr = expression[idx]
        lineno = dlines[idx]
        X[lineno] = expr
    
    # Adding control dependency expressions
    for idx in range(len(cdeps)):
        cdep = cdeps[idx]
        cline = clines[idx]
        for i in range(len(cdep)):
            if cdep[i]:
                expr = cdep[i]
                lineno = cline[i]
                X[lineno] = expr
    
    return X


def sensitivities(var, top_module, scope_module_map, ELABORATE_INFO):
    """
    Get sensitivities for a variable.
    
    Args:
        var: Variable triplet
        top_module: Top-level module name
        scope_module_map: Scope to module mapping
        ELABORATE_INFO: Elaborated module information
        
    Returns:
        list: Sensitivity list
    """
    scope = var[1]
    module = top_module if not scope else scope_module_map[scope]
    
    # Return empty list if module not found
    if module not in ELABORATE_INFO:
        return []
    
    var_def_chain = ELABORATE_INFO[module].get('var_def_chain', {})
    v = var[2]
    
    if v not in var_def_chain:
        return []
    
    return var_def_chain[v].get('Sensitivity', [])


def tcomplexity(var, top_module, scope_module_map, ELABORATE_INFO):
    """
    Calculate temporal complexity for a variable.
    
    Args:
        var: Variable triplet
        top_module: Top-level module name
        scope_module_map: Scope to module mapping
        ELABORATE_INFO: Elaborated module information
        
    Returns:
        int: Temporal complexity measure
    """
    scope = var[1]
    module = top_module if not scope else scope_module_map[scope]
    var_def_chain = ELABORATE_INFO[module]['var_def_chain']
    v = var[2]
    
    complexity = 0
    
    try:
        expressions_list = var_def_chain[v]['Expressions']
        for expr in expressions_list:
            code = generate_code(expr)
            complexity += len(code)
    except KeyError:
        pass
    
    return complexity


def temporal(var, top_module, scope_module_map, ELABORATE_INFO):
    """
    Get temporal information for a variable.
    
    Args:
        var: Variable triplet
        top_module: Top-level module name
        scope_module_map: Scope to module mapping
        ELABORATE_INFO: Elaborated module information
        
    Returns:
        bool: Whether variable has temporal (clocked) behavior
    """
    scope = var[1]
    module = top_module if not scope else scope_module_map[scope]
    var_def_chain = ELABORATE_INFO[module]['var_def_chain']
    v = var[2]
    
    try:
        return var_def_chain[v]['Clocked']
    except KeyError:
        return False


def analyze_dependencies(cdfg_info):
    """
    Main function to analyze dependencies from CDFG information.
    
    Args:
        cdfg_info: Dictionary containing CDFG information
        
    Returns:
        dict: Analysis results including dependency information
    """
    dep_g = cdfg_info['dep_g']
    var_def_chain = cdfg_info['var_def_chain']
    var_use_chain = cdfg_info['var_use_chain']
    
    analysis = {
        'dependency_graph': dep_g,
        'variables': list(dep_g.nodes()),
        'num_variables': dep_g.number_of_nodes(),
        'num_dependencies': dep_g.number_of_edges(),
        'def_chain': var_def_chain,
        'use_chain': var_use_chain
    }
    
    # Compute additional metrics
    if dep_g.number_of_nodes() > 0:
        # Find strongly connected components
        analysis['scc'] = list(nx.strongly_connected_components(dep_g))
        
        # Compute PageRank
        try:
            analysis['pagerank'] = nx.pagerank(dep_g)
        except:
            analysis['pagerank'] = {}
    
    return analysis
