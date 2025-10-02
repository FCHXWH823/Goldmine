"""
Static Analysis Standalone Module

A standalone module for static analysis of Verilog designs.
Extracted from the Goldmine tool for independent use.

Main components:
- graph_builder: Build CDFGs and dependency graphs
- dependency_analyzer: Analyze variable dependencies
- graph_visualizer: Visualize graphs (requires pygraphviz)
- utils: Utility functions

Usage:
    from static_analysis_standalone import build_cdfg, analyze_dependencies
"""

from .graph_builder import build_cdfg, construct_CDFG, get_var_def_chain, get_var_use_chain, construct_var_dep_graph
from .dependency_analyzer import analyze_dependencies, cone_of_influence, dependencies, expressions, sensitivities
from .utils import generate_code, traverse_CDFG, get_root_node, get_leaf_nodes, gvn

# Try to import visualization functions (requires pygraphviz)
try:
    from .graph_visualizer import visualize_graph, plot_digraph, plot_digraphs, save_dependency_graph
    _VISUALIZATION_AVAILABLE = True
except ImportError:
    _VISUALIZATION_AVAILABLE = False
    visualize_graph = None
    plot_digraph = None
    plot_digraphs = None
    save_dependency_graph = None

__version__ = '1.0.0'
__author__ = 'Goldmine Team'

__all__ = [
    # Main functions
    'build_cdfg',
    'analyze_dependencies',
    
    # Graph builder functions
    'construct_CDFG',
    'get_var_def_chain',
    'get_var_use_chain',
    'construct_var_dep_graph',
    
    # Dependency analyzer functions
    'cone_of_influence',
    'dependencies',
    'expressions',
    'sensitivities',
    
    # Utility functions
    'generate_code',
    'traverse_CDFG',
    'get_root_node',
    'get_leaf_nodes',
    'gvn',
]

# Add visualization functions if available
if _VISUALIZATION_AVAILABLE:
    __all__.extend([
        'visualize_graph',
        'plot_digraph',
        'plot_digraphs',
        'save_dependency_graph',
    ])
