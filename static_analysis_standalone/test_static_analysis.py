#!/usr/bin/env python
"""
Simple Test Script for Static Analysis Standalone Module

This script performs basic tests on the static analysis module.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from static_analysis_standalone import (
            build_cdfg, analyze_dependencies,
            construct_CDFG, get_var_def_chain, get_var_use_chain,
            construct_var_dep_graph, cone_of_influence, dependencies,
            expressions, sensitivities,
            generate_code, traverse_CDFG,
            get_root_node, get_leaf_nodes, gvn
        )
        print("  ✓ Core imports successful")
        
        # Try visualizer imports (may fail without pygraphviz)
        try:
            from static_analysis_standalone import visualize_graph, plot_digraph, plot_digraphs, save_dependency_graph
            print("  ✓ Visualization imports successful")
        except ImportError as e:
            print(f"  ⚠ Visualization imports skipped (missing pygraphviz): {e}")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False


def test_utils():
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    try:
        from static_analysis_standalone.utils import gvn, fill_color
        
        # Test gvn function
        v = ['', 'scope', 'var']
        result = gvn(v, 1)
        assert result == 'scope.var', f"Expected 'scope.var', got '{result}'"
        
        # Test fill_color function
        color = fill_color('IfStatement')
        assert color == 'springgreen', f"Expected 'springgreen', got '{color}'"
        
        color = fill_color('UnknownType')
        assert color == 'white', f"Expected 'white', got '{color}'"
        
        print("  ✓ Utility functions work correctly")
        return True
    except Exception as e:
        print(f"  ✗ Utility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_operations():
    """Test basic graph operations."""
    print("\nTesting graph operations...")
    
    try:
        import networkx as nx
        from static_analysis_standalone.utils import get_root_node, get_leaf_nodes
        
        # Create a simple test graph
        G = nx.DiGraph()
        G.add_edge('A', 'B')
        G.add_edge('B', 'C')
        G.add_edge('B', 'D')
        
        # Test root node
        root = get_root_node(G)
        assert root == ['A'], f"Expected ['A'], got {root}"
        
        # Test leaf nodes
        leaves = get_leaf_nodes(G)
        assert set(leaves) == {'C', 'D'}, f"Expected ['C', 'D'], got {leaves}"
        
        print("  ✓ Graph operations work correctly")
        return True
    except Exception as e:
        print(f"  ✗ Graph test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependency_graph():
    """Test dependency graph construction."""
    print("\nTesting dependency graph construction...")
    
    try:
        from static_analysis_standalone.graph_builder import construct_var_dep_graph
        
        # Create simple def and use chains
        var_def_chain = {
            'a': {'DDeps': [['b', 'c']], 'CDeps': [], 'Expressions': [], 
                  'DLines': [], 'CLines': [], 'Clocked': False},
            'b': {'DDeps': [['d']], 'CDeps': [], 'Expressions': [],
                  'DLines': [], 'CLines': [], 'Clocked': False}
        }
        var_use_chain = {}
        
        dep_g = construct_var_dep_graph(var_def_chain, var_use_chain)
        
        # Check graph properties
        # The graph should have nodes for defined variables and their dependencies
        assert dep_g.number_of_nodes() >= 2, f"Expected at least 2 nodes, got {dep_g.number_of_nodes()}"
        assert dep_g.has_edge('b', 'a'), "Expected edge from b to a"
        assert dep_g.has_edge('c', 'a'), "Expected edge from c to a"
        
        print(f"  ✓ Dependency graph construction works correctly ({dep_g.number_of_nodes()} nodes, {dep_g.number_of_edges()} edges)")
        return True
    except Exception as e:
        print(f"  ✗ Dependency graph test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Static Analysis Standalone Module - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Utils", test_utils()))
    results.append(("Graph Operations", test_graph_operations()))
    results.append(("Dependency Graph", test_dependency_graph()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:.<40} {status}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
