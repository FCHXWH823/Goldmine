# Quick Start Guide

## Installation

1. **Install system dependencies**:

**Icarus Verilog** (required for parsing Verilog):
```bash
# Ubuntu/Debian
sudo apt-get install iverilog

# macOS
brew install icarus-verilog
```

**Graphviz** (optional, for visualization):
```bash
# Ubuntu/Debian
sudo apt-get install graphviz graphviz-dev

# macOS
brew install graphviz
```

2. **Install Python dependencies**:

```bash
pip install -r requirements.txt
```

For visualization support (optional), also install:
```bash
pip install pygraphviz
```

## Basic Usage

### 1. Simple Analysis

Create a Python script to analyze a Verilog file:

```python
import sys
sys.path.insert(0, '..')  # Add parent directory to path

from static_analysis_standalone import build_cdfg, analyze_dependencies

# Parse and analyze
from pyverilog.vparser.parser import parse

ast, directives = parse(['examples/counter.v'])
cdfg_info = build_cdfg(ast, clocks=[], params={}, ports={})
analysis = analyze_dependencies(cdfg_info)

print(f"Found {analysis['num_variables']} variables")
print(f"Found {analysis['num_dependencies']} dependencies")
```

### 2. Using the Example Script

```bash
python example_usage.py examples/counter.v
```

This will:
- Parse the Verilog file
- Build CDFGs
- Analyze dependencies
- Generate visualizations (if pygraphviz is available)
- Save results to `./static_analysis_output/`

### 3. Running Tests

```bash
python test_static_analysis.py
```

## Examples

Two example Verilog files are provided in the `examples/` directory:

1. **counter.v** - A simple 8-bit counter with enable
2. **alu.v** - A simple ALU with 4 operations

## Output

The analysis produces several outputs:

### Without Visualization

- Variable definition chains
- Variable use chains
- Dependency graph (as NetworkX object)
- Number of variables and dependencies
- PageRank scores for variables

### With Visualization (requires pygraphviz)

- `cdfgs/` - Control/Data Flow Graphs as PNG images
- `dependency/` - Dependency graph visualization
- `paths/` - Path information in text format

## API Reference

### Main Functions

#### `build_cdfg(ast, clocks, params, ports)`
Build Control/Data Flow Graphs from parsed Verilog AST.

**Returns:** Dictionary with:
- `CDFGS` - List of CDFG graphs
- `PathSets` - Paths through each CDFG
- `var_def_chain` - Variable definition chains
- `var_use_chain` - Variable use chains
- `dep_g` - Dependency graph

#### `analyze_dependencies(cdfg_info)`
Analyze dependencies from CDFG information.

**Returns:** Dictionary with:
- `dependency_graph` - NetworkX DiGraph
- `variables` - List of all variables
- `num_variables` - Number of variables
- `num_dependencies` - Number of dependency edges
- `pagerank` - PageRank scores (if graph has nodes)

#### `visualize_graph(cdfg_info, output_dir)`
Generate visualizations (requires pygraphviz).

## Tips

1. **Memory Usage**: For large designs, the analysis may consume significant memory
2. **Clock Signals**: Provide clock signal names for more accurate temporal analysis
3. **Modules**: The analysis works on a per-module basis
4. **Dependencies**: Only networkx and pyverilog are required for basic analysis

## Troubleshooting

### Icarus Verilog Not Found

If you get an error about `iverilog` not being found:
1. Install Icarus Verilog (see Installation section)
2. Make sure it's in your PATH: `which iverilog`

### Import Errors

If you get import errors, make sure the parent directory is in your Python path:
```python
import sys
sys.path.insert(0, '/path/to/Goldmine')
```

### Visualization Not Working

If visualization doesn't work:
1. Check if pygraphviz is installed: `python -c "import pygraphviz"`
2. Install graphviz system package first, then pygraphviz
3. The analysis will still work without visualization

### Parse Errors

If Verilog parsing fails:
1. Make sure your Verilog file is syntactically correct
2. Use Verilog-2001 syntax (SystemVerilog may not be fully supported)
3. Check for `include directives and provide include paths if needed
