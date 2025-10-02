#!/usr/bin/env python
"""
Demo Script - Static Analysis Standalone Module

This script demonstrates the API without requiring Verilog parsing.
It creates synthetic data structures to show how the module works.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from static_analysis_standalone import (
    construct_var_dep_graph,
    analyze_dependencies,
    get_root_node,
    get_leaf_nodes,
    gvn
)

import networkx as nx


def demo_basic_usage():
    """Demonstrate basic usage of the static analysis module."""
    print("=" * 70)
    print("Static Analysis Standalone Module - Demo")
    print("=" * 70)
    
    # 1. Create sample variable definition and use chains
    print("\n1. Creating sample variable definition chains...")
    print("-" * 70)
    
    var_def_chain = {
        'count': {
            'DDeps': [['next_count']],
            'CDeps': [['rst']],
            'Expressions': ['count <= next_count'],
            'DLines': [23],
            'CLines': [[21]],
            'Clocked': True
        },
        'next_count': {
            'DDeps': [['count', 'enable']],
            'CDeps': [['enable']],
            'Expressions': ['next_count = count + 1', 'next_count = count'],
            'DLines': [14, 16],
            'CLines': [[13, 15]],
            'Clocked': False
        },
        'enable': {
            'DDeps': [[]],
            'CDeps': [],
            'Expressions': [],
            'DLines': [],
            'CLines': [],
            'Clocked': False
        }
    }
    
    var_use_chain = {
        'count': ['next_count'],
        'next_count': ['count'],
        'enable': ['next_count']
    }
    
    print("Variables defined:")
    for var in var_def_chain.keys():
        print(f"  - {var}")
    
    # 2. Build dependency graph
    print("\n2. Building variable dependency graph...")
    print("-" * 70)
    
    dep_g = construct_var_dep_graph(var_def_chain, var_use_chain)
    
    print(f"Nodes (variables): {dep_g.number_of_nodes()}")
    print(f"Edges (dependencies): {dep_g.number_of_edges()}")
    
    print("\nDependencies:")
    for src, dst in dep_g.edges():
        print(f"  {src} → {dst}")
    
    # 3. Analyze dependencies
    print("\n3. Analyzing dependencies...")
    print("-" * 70)
    
    cdfg_info = {
        'CDFGS': [],
        'PathSets': [],
        'var_def_chain': var_def_chain,
        'var_use_chain': var_use_chain,
        'dep_g': dep_g,
        'MODINSTS': []
    }
    
    analysis = analyze_dependencies(cdfg_info)
    
    print(f"Number of variables: {analysis['num_variables']}")
    print(f"Number of dependencies: {analysis['num_dependencies']}")
    
    if 'pagerank' in analysis and analysis['pagerank']:
        print("\nVariable importance (PageRank):")
        sorted_vars = sorted(analysis['pagerank'].items(), 
                           key=lambda x: x[1], reverse=True)
        for var, rank in sorted_vars:
            print(f"  {var}: {rank:.4f}")
    
    # 4. Demonstrate utility functions
    print("\n4. Demonstrating utility functions...")
    print("-" * 70)
    
    # Test gvn function
    var_triplet = ['', 'module1', 'signal_a']
    var_name = gvn(var_triplet, 1)
    print(f"Variable name from triplet {var_triplet}: {var_name}")
    
    # Test graph functions
    sample_graph = nx.DiGraph()
    sample_graph.add_edges_from([
        ('input', 'logic1'),
        ('logic1', 'logic2'),
        ('logic2', 'output'),
        ('logic1', 'output')
    ])
    
    roots = get_root_node(sample_graph)
    leaves = get_leaf_nodes(sample_graph)
    
    print(f"\nSample graph:")
    print(f"  Root nodes: {roots}")
    print(f"  Leaf nodes: {leaves}")
    print(f"  Edges: {list(sample_graph.edges())}")
    
    # 5. Summary
    print("\n" + "=" * 70)
    print("Demo Summary")
    print("=" * 70)
    print(f"✓ Successfully demonstrated static analysis functionality")
    print(f"✓ Analyzed {analysis['num_variables']} variables")
    print(f"✓ Found {analysis['num_dependencies']} dependencies")
    print(f"\nNote: This demo uses synthetic data.")
    print(f"For real Verilog analysis, use example_usage.py with iverilog installed.")
    print("=" * 70)


if __name__ == '__main__':
    demo_basic_usage()
