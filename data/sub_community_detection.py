import networkx as nx
import os
import pandas as pd
from config import community_id, community_dot_file_path, sub_community_analysis_output_dir
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
import os
import pandas as pd


def extract_community_from_dot(community_id, community_dot_file_path, sub_community_analysis_output_dir,
                               include_indirect_accessibility=True):
    """
    Extracts nodes and edges related to a specific community from a DOT file and saves it to a new DOT file.

    Parameters:
    - community_id: The ID of the community to extract
    - community_dot_file_path: Path to the original DOT file
    - sub_community_analysis_output_dir: Directory where the new DOT file and Excel file will be saved
    - include_indirect_accessibility: Boolean to include indirect (dashed) edges or not.
                                      True = include all edges, False = only include solid edges.
    """

    # Ensure the output directory exists
    os.makedirs(sub_community_analysis_output_dir, exist_ok=True)

    # Load the graph from the existing DOT file
    graph = nx.drawing.nx_pydot.read_dot(community_dot_file_path)

    # If indirect accessibility is not included, remove all dashed edges
    if not include_indirect_accessibility:
        edges_to_remove = [(u, v) for u, v, data in graph.edges(data=True) if data.get('style') == 'dashed']
        graph.remove_edges_from(edges_to_remove)
        print(f"Removed {len(edges_to_remove)} dashed (indirect) edges.")

    # Define the path for the Excel file within the output directory
    excel_file_path = os.path.join(sub_community_analysis_output_dir, "Sub-Community_Input.xlsx")

    # Load the Excel file to get node-community mapping
    df = pd.read_excel(excel_file_path)

    # Filter the DataFrame to get nodes belonging to the specified community
    community_nodes = df[df['Community ID'] == community_id]['Node ID'].tolist()

    # Create a subgraph with only the nodes from the specified community
    subgraph = graph.subgraph(community_nodes).copy()

    # Prepare the new DOT file path
    base_name = os.path.basename(community_dot_file_path)
    accessibility_tag = "with_indirect_edges" if include_indirect_accessibility else "without_IA"
    new_dot_file_name = f"{os.path.splitext(base_name)[0]}_community_id_{community_id}_{accessibility_tag}.dot"
    new_dot_file_path = os.path.join(sub_community_analysis_output_dir, new_dot_file_name)

    # Save the subgraph to a new DOT file
    nx.drawing.nx_pydot.write_dot(subgraph, new_dot_file_path)

    print(f"New DOT file saved to: {new_dot_file_path}")
    print(f"Excel file path used: {excel_file_path}")

def extract_all_communities_from_dot(community_dot_file_path, sub_community_analysis_output_dir,
                                     include_indirect_accessibility=True):
    """
    Extracts and saves DOT files for all unique community IDs found in the Excel file.

    Parameters:
    - community_dot_file_path: Path to the original DOT file
    - sub_community_analysis_output_dir: Directory where the new DOT files will be saved
    - include_indirect_accessibility: Boolean to include indirect (dashed) edges or not.
                                      True = include all edges, False = only include solid edges.
    """

    # Define the path for the Excel file within the output directory
    excel_file_path = os.path.join(sub_community_analysis_output_dir, "Sub-Community_Input.xlsx")

    # Load the Excel file to get node-community mapping
    df = pd.read_excel(excel_file_path)

    # Get unique community IDs
    community_ids = df['Community ID'].unique()

    # Extract each community
    for community_id in community_ids:
        print(f"Processing community ID: {community_id}")
        extract_community_from_dot(community_id, community_dot_file_path, sub_community_analysis_output_dir,
                                   include_indirect_accessibility)


def plot_and_save_communities_with_betweenness(sub_community_analysis_output_dir):
    """
    Plots and saves DOT graphs in the specified directory with nodes colored based on betweenness centrality.

    Parameters:
    - sub_community_analysis_output_dir: Directory where the DOT files for sub-communities are saved
    """
    # Get a list of DOT files in the output directory
    dot_files = [f for f in os.listdir(sub_community_analysis_output_dir) if f.endswith('.dot')]

    # Define a color map for centrality groups
    color_map = list(mcolors.TABLEAU_COLORS.values())

    for dot_file in dot_files:
        # Load the graph from the DOT file
        dot_file_path = os.path.join(sub_community_analysis_output_dir, dot_file)
        graph = nx.drawing.nx_pydot.read_dot(dot_file_path)

        # Calculate betweenness centrality
        betweenness_centrality = nx.betweenness_centrality(graph)

        # Get unique centrality values for coloring
        unique_centralities = list(set(betweenness_centrality.values()))
        unique_centralities.sort()  # Sort to assign colors consistently

        # Create a mapping from centrality to color
        centrality_color_map = {cent: color_map[i % len(color_map)] for i, cent in enumerate(unique_centralities)}

        # Assign colors to nodes based on their betweenness centrality
        node_colors = [centrality_color_map[betweenness_centrality[node]] for node in graph.nodes()]

        # Use node labels from the DOT file
        node_labels = {node: graph.nodes[node].get('label', node) for node in graph.nodes()}

        # Plot the graph
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(graph)  # Layout for better visualization
        nx.draw(graph, pos, node_color=node_colors, labels=node_labels, with_labels=True, font_size=8,
                node_size=300, edge_color="gray")

        # Define the path to save the plot image
        image_file_name = f"{os.path.splitext(dot_file)[0]}_betweenness_plot.png"
        image_file_path = os.path.join(sub_community_analysis_output_dir, image_file_name)

        # Save the plot as an image
        plt.savefig(image_file_path, format="png")
        plt.close()

        print(f"Graph saved as image: {image_file_path}")


from networkx.algorithms.community import girvan_newman
from networkx.algorithms.community.quality import modularity


def detect_communities_and_calculate_centrality_max_modularity_raw(community_dot_file_path, output_dir):
    """
    Detects communities in the graph using the Girvan-Newman algorithm and selects the community split
    with the highest modularity. Calculates raw (non-normalized) degree and betweenness centrality for
    each node and saves the results to an Excel file.

    Parameters:
    - community_dot_file_path: Path to the DOT file representing the graph.
    - output_dir: Directory where the results Excel file will be saved.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the graph from the DOT file
    graph = nx.drawing.nx_pydot.read_dot(community_dot_file_path)

    # Initialize Girvan-Newman generator
    community_generator = girvan_newman(graph)

    # Variables to store the best partition and its modularity
    best_partition = None
    max_modularity = -1

    # Iterate through community splits to calculate modularity
    for communities in community_generator:
        # Convert communities to a list of sets
        community_list = [set(c) for c in communities]

        # Calculate modularity for the current split
        current_modularity = modularity(graph, community_list)
        print(f"Detected {len(communities)} communities with modularity: {current_modularity:.4f}")

        # Update the best partition if the modularity improves
        if current_modularity > max_modularity:
            max_modularity = current_modularity
            best_partition = community_list
        else:
            # Stop iterating when modularity starts decreasing
            break

    print(f"Best modularity: {max_modularity:.4f} with {len(best_partition)} communities.")

    # Prepare a DataFrame to store results
    results = []

    # Calculate raw centrality measures for the best partition
    for i, community in enumerate(best_partition):
        # Extract the subgraph for the community
        subgraph = graph.subgraph(community)

        # Calculate raw degree (number of edges per node)
        raw_degrees = dict(subgraph.degree())

        # Calculate raw betweenness centrality (not normalized)
        raw_betweenness_centrality = nx.betweenness_centrality(subgraph, normalized=False)

        # Add the results to the DataFrame
        for node in subgraph.nodes():
            results.append({
                "Community ID": i + 1,
                "Node ID": node,
                "Raw Degree": raw_degrees[node],  # Raw degree
                "Raw Betweenness Centrality": raw_betweenness_centrality[node]  # Raw betweenness
            })

    # Convert results to a DataFrame
    results_df = pd.DataFrame(results)

    # Define the path for the output Excel file
    excel_file_path = os.path.join(output_dir, "Community_Centrality_Analysis_Max_Modularity_Raw.xlsx")

    # Save the DataFrame to an Excel file
    results_df.to_excel(excel_file_path, index=False)
    print(f"Centrality analysis saved to: {excel_file_path}")

if __name__ == "__main__":

    # # Call the function to extract the community and create a new dot file
    # extract_community_from_dot(community_id, community_dot_file_path, sub_community_analysis_output_dir,
    #                            include_indirect_accessibility=False)

    # # Call the function to extract all communities and create individual DOT files
    # extract_all_communities_from_dot(community_dot_file_path, sub_community_analysis_output_dir,
    #                                  include_indirect_accessibility=True)
    #
    # # Plot all communities with color-coded betweenness centrality
    # plot_and_save_communities_with_betweenness(sub_community_analysis_output_dir)

    # Call the function to detect communities using Girvan-Newman with modularity optimization
    detect_communities_and_calculate_centrality_max_modularity_raw(
        community_dot_file_path, sub_community_analysis_output_dir
    )

    # Extract all communities as DOT files
    extract_all_communities_from_dot(community_dot_file_path, sub_community_analysis_output_dir,
                                     include_indirect_accessibility=False)

    # Plot all communities with color-coded betweenness centrality
    plot_and_save_communities_with_betweenness(sub_community_analysis_output_dir)