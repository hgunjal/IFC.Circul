import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import shutil
import subprocess
import pandas as pd
import json
import os



def load_graph_from_dot(dot_file_path):
    """
    Loads a graph from a DOT file, ignoring edges with wall attb.
    """
    # Load the graph from the DOT file
    graph = nx.drawing.nx_pydot.read_dot(dot_file_path)

    # Identify and remove edges with style='dashed'
    edges_to_remove = [(u, v) for u, v, data in graph.edges(data=True) if data.get('style') == 'dashed']
    graph.remove_edges_from(edges_to_remove)

    print(f"Ignored {len(edges_to_remove)} edges with style=dashed")

    return graph


def calculate_edge_betweenness(graph):
    """
    Calculates edge betweenness for all edges in the graph using the Girvan-Newman algorithm.
    """
    return nx.edge_betweenness_centrality(graph)


def remove_high_betweenness_edges(graph, edge_betweenness, threshold=0.07):
    """
    Removes edges from the graph that have a betweenness centrality higher than the threshold.
    """
    # Ensure that the threshold is within a sensible range
    if threshold < 0 or threshold > 1:
        raise ValueError("Threshold should be between 0 and 1.")

    # Identify edges with betweenness centrality higher than the threshold
    edges_to_remove = [(u, v) for u, v, _ in graph.edges(keys=True)
                       if edge_betweenness.get((u, v, 0), 0) > threshold]

    # Remove the identified edges from the graph
    graph.remove_edges_from(edges_to_remove)
    print(f"Removed {len(edges_to_remove)} edges with betweenness centrality above {threshold}")




def visualize_graph(graph, json_file_path, edge_betweenness):
    """
    Visualizes the graph using matplotlib, renames nodes using a JSON file,
    and displays edge betweenness centrality values as edge labels.
    """
    # Load the JSON file that contains node renaming information
    with open(json_file_path, 'r') as f:
        node_details = json.load(f)

    # Rename nodes for visualization
    rename_mapping = {node: node_details[node].get("Space Long Name", node) for node in graph.nodes if
                      node in node_details}
    graph_for_viz = nx.relabel_nodes(graph, rename_mapping, copy=True)  # Create a renamed copy for visualization

    plt.figure(figsize=(12, 12))  # Increased figure size for better visibility
    pos = nx.spring_layout(graph_for_viz)  # Positions for all nodes

    # Dynamically calculate node sizes based on label lengths
    node_labels = {node: rename_mapping.get(node, node) for node in graph_for_viz.nodes}
    node_sizes = [len(label) * 200 for label in node_labels.values()]  # Scale node size based on label length

    # Draw nodes and edges
    nx.draw(graph_for_viz, pos, with_labels=True, labels=node_labels, node_size=node_sizes,
            node_color="skyblue", font_size=10, font_weight="bold", edge_color="gray")

    # Prepare edge labels with betweenness values
    edge_labels = {}
    for (u, v, _), centrality in edge_betweenness.items():
        # Use renamed node labels for displaying betweenness
        u_name = rename_mapping.get(u, u)
        v_name = rename_mapping.get(v, v)
        edge_labels[(u_name, v_name)] = f"{centrality:.3f}"  # Formatting the betweenness to 3 decimal places

    # Draw edge labels (betweenness centrality)
    nx.draw_networkx_edge_labels(graph_for_viz, pos, edge_labels=edge_labels)

    plt.title("Graph Visualization (with edge betweenness centrality and resized nodes)")
    plt.show()


def visualize_filtered_graph(graph, json_file_path, edge_betweenness, threshold=0.07):
    """
    Visualizes the graph after removing high betweenness edges and isolated nodes.

    Parameters:
    - graph: NetworkX graph object
    - json_file_path: Path to JSON file containing node details
    - edge_betweenness: Dictionary of edge betweenness centrality values
    - threshold: Threshold for removing high betweenness edges (default: 0.07)
    """
    import networkx as nx
    import matplotlib.pyplot as plt

    # Create a copy of the graph to avoid modifying the original
    filtered_graph = graph.copy()

    # Remove high betweenness edges
    edges_to_remove = [(u, v) for u, v, _ in filtered_graph.edges(keys=True)
                       if edge_betweenness.get((u, v, 0), 0) > threshold]
    filtered_graph.remove_edges_from(edges_to_remove)

    # Remove isolated nodes (nodes with no edges)
    isolated_nodes = list(nx.isolates(filtered_graph))
    filtered_graph.remove_nodes_from(isolated_nodes)

    # Load the JSON file that contains node renaming information
    with open(json_file_path, 'r') as f:
        node_details = json.load(f)

    # Rename nodes for visualization (only for nodes that remain in the filtered graph)
    rename_mapping = {node: node_details[node].get("Space Long Name", node)
                      for node in filtered_graph.nodes if node in node_details}
    graph_for_viz = nx.relabel_nodes(filtered_graph, rename_mapping, copy=True)

    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(graph_for_viz, k=1, iterations=50)  # Adjusted layout parameters

    # Calculate node sizes based on label lengths
    node_labels = {node: rename_mapping.get(node, node) for node in graph_for_viz.nodes}
    node_sizes = [len(label) * 200 for label in node_labels.values()]

    # Draw nodes and edges
    nx.draw(graph_for_viz, pos,
            with_labels=True,
            labels=node_labels,
            node_size=node_sizes,
            node_color="skyblue",
            font_size=10,
            font_weight="bold",
            edge_color="gray")

    # Prepare edge labels with betweenness values for remaining edges
    edge_labels = {}
    for (u, v, _), centrality in edge_betweenness.items():
        # Skip edges that were removed due to high betweenness
        if centrality <= threshold:
            u_name = rename_mapping.get(u, u)
            v_name = rename_mapping.get(v, v)
            if u_name in graph_for_viz.nodes and v_name in graph_for_viz.nodes:
                edge_labels[(u_name, v_name)] = f"{centrality:.3f}"

    # Draw edge labels
    nx.draw_networkx_edge_labels(graph_for_viz, pos, edge_labels=edge_labels)

    # Add title with statistics
    original_nodes = len(graph.nodes)
    remaining_nodes = len(filtered_graph.nodes)
    removed_edges = len(edges_to_remove)

    plt.title(f"Filtered Graph Visualization\n"
              f"Removed {removed_edges} high betweenness edges (threshold: {threshold})\n"
              f"Removed {len(isolated_nodes)} isolated nodes\n"
              f"Remaining: {remaining_nodes}/{original_nodes} nodes")

    plt.show()

    # Print summary statistics
    print(f"\nVisualization Summary:")
    print(f"Original nodes: {original_nodes}")
    print(f"Remaining nodes: {remaining_nodes}")
    print(f"Removed edges: {removed_edges}")
    print(f"Removed isolated nodes: {len(isolated_nodes)}")


def save_cluster_visualizations(graph, json_file_path, edge_betweenness, threshold, output_folder, graph_name):
    """
    Identifies clusters in the filtered graph and saves each cluster as a separate PNG file
    with uniquely colored nodes.

    Parameters:
    - graph: NetworkX graph object
    - json_file_path: Path to JSON file containing node details
    - edge_betweenness: Dictionary of edge betweenness centrality values
    - threshold: Threshold for removing high betweenness edges
    - output_folder: Folder to save the PNG files
    - graph_name: Name of the graph for file naming
    """
    import networkx as nx
    import matplotlib.pyplot as plt
    import os
    from matplotlib.colors import TABLEAU_COLORS

    # Create output directory if it doesn't exist
    cluster_output_folder = os.path.join(output_folder, 'clusters')
    os.makedirs(cluster_output_folder, exist_ok=True)

    # Create a copy of the graph and remove high betweenness edges
    filtered_graph = graph.copy()
    edges_to_remove = [(u, v) for u, v, _ in filtered_graph.edges(keys=True)
                       if edge_betweenness.get((u, v, 0), 0) > threshold]
    filtered_graph.remove_edges_from(edges_to_remove)

    # Remove isolated nodes
    isolated_nodes = list(nx.isolates(filtered_graph))
    filtered_graph.remove_nodes_from(isolated_nodes)

    # Load node details from JSON
    with open(json_file_path, 'r') as f:
        node_details = json.load(f)

    # Get connected components (clusters)
    clusters = list(nx.connected_components(filtered_graph))

    # Get a list of distinct colors from matplotlib
    colors = list(TABLEAU_COLORS.values())

    # Process each cluster
    for cluster_idx, cluster_nodes in enumerate(clusters):
        # Create a subgraph for this cluster
        subgraph = filtered_graph.subgraph(cluster_nodes).copy()

        # Create the visualization
        plt.figure(figsize=(12, 12))

        # Rename nodes for this cluster
        rename_mapping = {node: node_details[node].get("Space Long Name", node)
                          for node in subgraph.nodes if node in node_details}
        viz_graph = nx.relabel_nodes(subgraph, rename_mapping, copy=True)

        # Calculate layout
        pos = nx.spring_layout(viz_graph, k=1, iterations=50)

        # Calculate node sizes
        node_labels = {node: rename_mapping.get(node, node) for node in viz_graph.nodes}
        node_sizes = [len(label) * 200 for label in node_labels.values()]

        # Draw nodes and edges with cluster-specific color
        node_color = colors[cluster_idx % len(colors)]
        nx.draw(viz_graph, pos,
                with_labels=True,
                labels=node_labels,
                node_size=node_sizes,
                node_color=node_color,
                font_size=10,
                font_weight="bold",
                edge_color="gray")

        # Add edge labels
        edge_labels = {}
        for (u, v, _), centrality in edge_betweenness.items():
            if centrality <= threshold:
                u_name = rename_mapping.get(u, u)
                v_name = rename_mapping.get(v, v)
                if u_name in viz_graph.nodes and v_name in viz_graph.nodes:
                    edge_labels[(u_name, v_name)] = f"{centrality:.3f}"

        nx.draw_networkx_edge_labels(viz_graph, pos, edge_labels=edge_labels)

        # Add title with cluster information
        plt.title(f"Cluster {cluster_idx + 1}\n"
                  f"Nodes: {len(cluster_nodes)}")

        # Save the cluster visualization
        output_file = os.path.join(cluster_output_folder,
                                   f"{graph_name}_sub_cluster_n={cluster_idx + 1}.png")
        plt.savefig(output_file, bbox_inches='tight', dpi=300)
        plt.close()

        print(f"Saved cluster {cluster_idx + 1} with {len(cluster_nodes)} nodes to {output_file}")

    # Print summary
    print(f"\nVisualization Summary:")
    print(f"Total clusters identified: {len(clusters)}")
    print(f"Clusters saved to: {cluster_output_folder}")
    print(f"Files saved: {[f'{graph_name}_sub_cluster_n={i + 1}.png' for i in range(len(clusters))]}")


def export_clusters_to_excel(graph, json_file_path, edge_betweenness, threshold, output_folder, graph_name):
    """
    Exports cluster information and edge betweenness centrality to Excel file with two sheets.

    Parameters:
    - graph: NetworkX graph object
    - json_file_path: Path to JSON file containing node details
    - edge_betweenness: Dictionary of edge betweenness centrality values
    - threshold: Threshold for removing high betweenness edges
    - output_folder: Folder to save the Excel file
    - graph_name: Name of the graph for file naming
    """
    # Create a copy of the graph and remove high betweenness edges
    filtered_graph = graph.copy()
    edges_to_remove = [(u, v) for u, v, _ in filtered_graph.edges(keys=True)
                       if edge_betweenness.get((u, v, 0), 0) > threshold]
    filtered_graph.remove_edges_from(edges_to_remove)

    # Remove isolated nodes
    isolated_nodes = list(nx.isolates(filtered_graph))
    filtered_graph.remove_nodes_from(isolated_nodes)

    # Load node details from JSON
    with open(json_file_path, 'r') as f:
        node_details = json.load(f)

    # Get connected components (clusters)
    clusters = list(nx.connected_components(filtered_graph))

    # Prepare cluster data for DataFrame
    cluster_data = []
    for cluster_idx, cluster_nodes in enumerate(clusters):
        for node in cluster_nodes:
            node_info = node_details.get(node, {})
            cluster_data.append({
                'Cluster ID': cluster_idx + 1,
                'Cluster Size': len(cluster_nodes),
                'Node ID': node,
                'Space Name': node_info.get('Space Long Name', 'N/A')
            })

    # Create cluster DataFrame
    df_clusters = pd.DataFrame(cluster_data)
    df_clusters = df_clusters.sort_values(['Cluster ID', 'Space Name'])

    # Prepare edge betweenness data
    edge_data = []
    for (u, v, _), centrality in edge_betweenness.items():
        # Get space names for the nodes
        u_name = node_details.get(u, {}).get('Space Long Name', u)
        v_name = node_details.get(v, {}).get('Space Long Name', v)
        edge_data.append({
            'Edge Between Nodes': f"{u_name} - {v_name}",
            'Betweenness Centrality Value': centrality
        })

    # Create edge betweenness DataFrame
    df_edges = pd.DataFrame(edge_data)
    df_edges = df_edges.sort_values('Betweenness Centrality Value', ascending=False)

    # Save to Excel with both sheets
    excel_path = os.path.join(output_folder, f"{graph_name}_cluster_analysis.xlsx")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Write cluster data
        df_clusters.to_excel(writer, sheet_name='Cluster Information', index=False)

        # Write edge betweenness data
        df_edges.to_excel(writer, sheet_name='Edge Betweenness Centrality', index=False)

        # Auto-adjust column widths for both sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column = list(column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

    print(f"\nExcel export complete:")
    print(f"File saved to: {excel_path}")
    print(f"Total clusters: {len(clusters)}")
    print(f"Total nodes: {len(df_clusters)}")
    print(f"Total edges analyzed: {len(df_edges)}")

if __name__ == "__main__":

    # Load the graph from a DOT file
    json_file = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC20-Office-Building_Output\AC20-Office-Building_space_info_dict.json'
    dot_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC20-Office-Building_Output\adjacent_rooms_graph_Spatial Proximity Graph - Office Building_Erdgeschoss.dot'
    json_file = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Output\NBU_MedicalClinic_Arch_space_info_dict.json'
    dot_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Output\adjacent_rooms_graph_Spatial Proximity Graph - Medical Clinic_First Floor.dot'
    graph = load_graph_from_dot(dot_file_path)
    # visualize_graph(graph, json_file)

    # Extract graph name from path
    graph_name, _ = os.path.splitext(os.path.basename(dot_file_path))

    # Calculate edge betweenness
    edge_betweenness = calculate_edge_betweenness(graph)
    print("Edge Betweenness Centrality:", edge_betweenness)



    t=0.14
    remove_high_betweenness_edges(graph, edge_betweenness, threshold=t)



    betweenness_values = list(edge_betweenness.values())
    print("Minimum Betweenness Centrality:", min(betweenness_values))
    print("Maximum Betweenness Centrality:", max(betweenness_values))
    print("Mean Betweenness Centrality:", np.mean(betweenness_values))


    visualize_graph(graph, json_file, edge_betweenness)
    visualize_filtered_graph(graph, json_file, edge_betweenness, threshold=t)
    # Create dynamic file paths based on graph name
    output_folder = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC20-Office-Building_Output\Community_Detection\without walls'
    output_folder = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Output\Community_Detection\without walls'

    os.makedirs(output_folder, exist_ok=True)  # Ensure the folder exists

    # Create path for cluster visualizations
    cluster_output_folder = os.path.join(output_folder, 'clusters')

    # Save cluster visualizations
    save_cluster_visualizations(graph, json_file, edge_betweenness,
                                 threshold=t, output_folder=output_folder,
                                 graph_name=graph_name)
    export_clusters_to_excel(graph, json_file, edge_betweenness, threshold=t, output_folder=output_folder,
                                graph_name=graph_name)