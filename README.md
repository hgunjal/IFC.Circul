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
   - `Girvan-Newman Clustering` to perform community detection and `Avg. Path Length` to perform centrality analysis

![Space-level Topological Analysis](https://github.com/user-attachments/assets/5a009e72-d360-4cc2-a91f-03d544f827c7)

## 📊 Sample Visualization

### 1. Building Model Visualization
![3D View of IFC Model](https://github.com/user-attachments/assets/79e6c552-e34b-468f-9140-e642bc4c0937)

*3D visualization of the IFC building model*

![Floor Plan View](https://github.com/user-attachments/assets/e0d5d04f-35ec-49c2-b571-093b5df5f2cd)

*Floor plan view of the IFC model*

### 2. Topological Analysis
![Space-level Topological Graph](https://github.com/user-attachments/assets/f4b3173e-877e-4a62-81cb-244547efba58)

*Space-level topological graph where:*
- Different node colors represent different building floors
- Green edges indicate exits
- Red edges represent stair accessibility
- Regular edges show horizontal accessibility between spaces

![Centrality Analysis](https://github.com/user-attachments/assets/fa38951b-7dc9-45f4-9e6e-8cb7a971b759)

*Centrality analysis performed in Gephi, highlighting nodes with highest betweenness centrality on the right side, indicating key circulation points in the building*


---
*For questions and support, please open an issue in the GitHub repository.*
