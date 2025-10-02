#!/usr/bin/env python
"""
Example Usage of Static Analysis Standalone Module

This script demonstrates how to use the static analysis functionality
to analyze a Verilog design.
"""

import sys
import os

# Import Pyverilog for parsing
try:
    from pyverilog.vparser.parser import parse
except ImportError:
    print("Error: pyverilog is required. Install with: pip install pyverilog")
    sys.exit(1)

# Import static analysis functions
from static_analysis_standalone import build_cdfg, analyze_dependencies, visualize_graph


def analyze_verilog_file(verilog_file, output_dir='./static_analysis_output'):
    """
    Analyze a Verilog file and generate static analysis reports.
    
    Args:
        verilog_file: Path to Verilog file
        output_dir: Directory for output files
    """
    print(f"Analyzing Verilog file: {verilog_file}")
    print("=" * 60)
    
    # Step 1: Parse the Verilog file
    print("\n1. Parsing Verilog file...")
    try:
        ast, directives = parse([verilog_file])
        print("   ✓ Parsing complete")
    except Exception as e:
        print(f"   ✗ Error parsing file: {e}")
        return
    
    # Step 2: Build CDFG
    print("\n2. Building Control/Data Flow Graphs...")
    try:
        # Note: You may need to specify clock signals and other parameters
        # For this example, we use empty lists
        clocks = []
        params = {}
        ports = {}
        
        cdfg_info = build_cdfg(ast, clocks, params, ports)
        
        print(f"   ✓ Built {len(cdfg_info['CDFGS'])} CDFGs")
        print(f"   ✓ Found {cdfg_info['dep_g'].number_of_nodes()} variables")
        print(f"   ✓ Found {cdfg_info['dep_g'].number_of_edges()} dependencies")
    except Exception as e:
        print(f"   ✗ Error building CDFG: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Analyze dependencies
    print("\n3. Analyzing dependencies...")
    try:
        analysis = analyze_dependencies(cdfg_info)
        
        print(f"   ✓ Analyzed {analysis['num_variables']} variables")
        print(f"   ✓ Found {analysis['num_dependencies']} dependencies")
        
        if 'pagerank' in analysis and analysis['pagerank']:
            # Show top 5 variables by PageRank
            top_vars = sorted(analysis['pagerank'].items(), 
                            key=lambda x: x[1], reverse=True)[:5]
            print("\n   Top 5 variables by importance (PageRank):")
            for var, rank in top_vars:
                print(f"     - {var}: {rank:.4f}")
    except Exception as e:
        print(f"   ✗ Error analyzing dependencies: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Visualize graphs
    print("\n4. Generating visualizations...")
    try:
        visualize_graph(cdfg_info, output_dir)
        print(f"   ✓ Visualizations saved to: {output_dir}")
    except Exception as e:
        print(f"   ✗ Error generating visualizations: {e}")
        print(f"   Note: Visualization requires graphviz to be installed")
        import traceback
        traceback.print_exc()
    
    # Step 5: Print summary
    print("\n" + "=" * 60)
    print("Analysis Summary:")
    print("=" * 60)
    print(f"Input file: {verilog_file}")
    print(f"Number of CDFGs: {len(cdfg_info['CDFGS'])}")
    print(f"Number of variables: {analysis['num_variables']}")
    print(f"Number of dependencies: {analysis['num_dependencies']}")
    print(f"Output directory: {output_dir}")
    print("\nAnalysis complete!")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py <verilog_file> [output_dir]")
        print("\nExample:")
        print("  python example_usage.py design.v")
        print("  python example_usage.py design.v ./my_output")
        sys.exit(1)
    
    verilog_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './static_analysis_output'
    
    if not os.path.exists(verilog_file):
        print(f"Error: File not found: {verilog_file}")
        sys.exit(1)
    
    analyze_verilog_file(verilog_file, output_dir)


if __name__ == '__main__':
    main()
