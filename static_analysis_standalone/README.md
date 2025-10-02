# Static Analysis Standalone Module

This directory contains standalone Python scripts for performing static analysis on Verilog designs.

## Overview

The static analysis module provides functionality to analyze Verilog code without requiring the full Goldmine tool chain. It includes:

- **CDFG (Control/Data Flow Graph) Construction**: Build control and data flow graphs from Verilog AST
- **Dependency Analysis**: Analyze variable dependencies (def-use chains)
- **Graph Visualization**: Generate visual representations of CDFGs and dependency graphs
- **Cone of Influence**: Compute the cone of influence for target variables

## Requirements

```bash
pip install networkx pyverilog pygraphviz numpy regex
```

## Core Components

### 1. `graph_builder.py`
Contains functions for building various graph representations:
- CDFG construction
- Variable dependency graph construction
- Module instantiation chains

### 2. `dependency_analyzer.py`
Analyzes variable dependencies:
- Def-use chain analysis
- Temporal dependencies
- Cone of influence computation

### 3. `graph_visualizer.py`
Generates visual representations:
- CDFG visualization
- Dependency graph plotting
- Path information extraction

### 4. `utils.py`
Utility functions:
- AST code generation
- Graph traversal algorithms
- Helper functions

## Usage Example

```python
from static_analysis_standalone.graph_builder import build_cdfg
from static_analysis_standalone.dependency_analyzer import analyze_dependencies
from static_analysis_standalone.graph_visualizer import visualize_graph

# Parse your Verilog file (using pyverilog)
from pyverilog.vparser.parser import parse

ast, directives = parse(['your_design.v'])

# Build CDFG
cdfg_info = build_cdfg(ast, clock_signals, params, ports)

# Analyze dependencies
dep_info = analyze_dependencies(cdfg_info)

# Visualize
visualize_graph(cdfg_info, output_dir='./output')
```

## Key Functions

### CDFG Construction
```python
from static_analysis_standalone.graph_builder import construct_CDFG

# Build CDFG from AST
cdfgs, modinsts = construct_CDFG(ast, cdfg_list, modinst_list, clocks, indent=0)
```

### Dependency Analysis
```python
from static_analysis_standalone.dependency_analyzer import get_var_def_chain, get_var_use_chain

# Get variable definition chains
var_def_chain = get_var_def_chain(cdfgs, path_sets, params)

# Get variable use chains
var_use_chain = get_var_use_chain(cdfgs, path_sets, params)
```

### Graph Visualization
```python
from static_analysis_standalone.graph_visualizer import plot_digraph

# Visualize dependency graph
plot_digraph([graph], output_path, ['graph_name'])
```

## Features

- **Independent Usage**: Can be used without the full Goldmine infrastructure
- **Modular Design**: Each component can be used independently
- **Graph-based Analysis**: Leverages NetworkX for efficient graph operations
- **Visualization**: Built-in support for graph visualization using Graphviz

## Note

This standalone module extracts the core static analysis functionality from Goldmine. For full assertion mining and verification capabilities, please use the complete Goldmine tool.
