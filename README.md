# IFC.Circul 🏗️

A Python package for extracting and analyzing space-level topological relationships from IFC (Industry Foundation Classes) building models.

## 📋 Overview

This project was developed as part of a master's thesis research at the Technical University of Munich.

### Thesis Details
- **Title**: Reasoning IFC Models for Space-level Circulation Design Rationale using Graph-based Analysis and Community Detection
- **Author**: Harshal Gunjal
- **Supervisor**: Jiabin Wu
- **Institution**: [Chair of Computational Modeling and Simulation](https://www.cee.ed.tum.de/cms/home/), [Technical University of Munich](https://www.tum.de/)

## ⚙️ Installation

### Prerequisites
- Git
- Anaconda Navigator
- PyCharm Community Edition
- [Gephi](https://gephi.org/)

### Required Packages
- IfcOpenShell
- Graphviz
- Trimesh
- rtree
- scipy
- pyglet
- NumPy
- NetworkX

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/hgunjal/IFC.Circul
   ```

2. Create and configure environment:
   - Launch Anaconda Navigator
   - Create a new environment
   - Install all required packages listed above

3. Open the project in PyCharm Community Edition

## 🚀 Usage

1. Configure Input/Output Settings
   - Open `config.py`
   - Set the input IFC file path
   - Configure output directories

2. Generate Topological Relationships
   - Run `ifc_to_csv_or_json.py`
   - This will create space-level topological relationships in JSON format

3. Create Graph Representation
   - Run `ifc_to_graph.py`
   - Converts the JSON file to a DOT graph file

4. Analyze Results
   - Open the generated DOT file using [Gephi](https://gephi.org/)
   - Perform graph analysis and visualization

![Space-level Topological Analysis](https://github.com/user-attachments/assets/5a009e72-d360-4cc2-a91f-03d544f827c7)

## 📊 Sample Visualization



---
*For questions and support, please open an issue in the GitHub repository.*
