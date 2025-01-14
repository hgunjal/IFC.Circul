import glob
from config import output_dir, json_file, dot_file_path, cd_output_folder
import networkx as nx
from networkx.drawing.nx_pydot import write_dot
import matplotlib.pyplot as plt
import pandas as pd
import json
import os


def analyze_communities(graph, json_file_path, output_folder, graph_name):
    """
    Analyzes communities in the graph using Girvan-Newman algorithm and creates visualizations.

    Parameters:
    - graph: NetworkX graph object
    - json_file_path: Path to JSON file containing node details
    - output_folder: Folder to save outputs
    - graph_name: Name of the graph for file naming
    """
    # Load node details from JSON
    with open(json_file_path, 'r') as f:
        node_details = json.load(f)

    # Get communities using Girvan-Newman
    communities_generator = nx.community.girvan_newman(graph)
    communities = list(communities_generator)

    # Modularity -> measures the strength of division of a network into modules
    # Calculate modularity for each community division
    modularity_data = []
    for k, comm in enumerate(communities):
        modularity = nx.community.modularity(graph, comm)
        modularity_data.append({
            'Community Split Index': k + 2,  # k+2 because Girvan-Newman starts with 2 communities
            'Modularity': modularity
        })

    # Create modularity DataFrame and export to Excel
    modularity_df = pd.DataFrame(modularity_data)
    excel_path = os.path.join(output_folder, f"{graph_name}_community_analysis.xlsx")

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Export modularity data
        modularity_df.to_excel(writer, sheet_name='Modularity Analysis', index=False)

        # Export community memberships with modularity score in sheet names
        for k, comm in enumerate(communities):
            # Calculate modularity for the current community division
            modularity = modularity_data[k]['Modularity']

            # Prepare community data
            community_data = []
            for i, community in enumerate(comm):
                for node in community:
                    node_info = node_details.get(node, {})
                    community_data.append({
                        'Community ID': i + 1,
                        'Node ID': node,
                        'Space Long Name': node_info.get('Space Long Name', 'N/A'),
                        'Space Name': node_info.get('Space Name', 'N/A')
                    })

            # Create and export DataFrame for this community division
            comm_df = pd.DataFrame(community_data)
            comm_df = comm_df.sort_values(['Community ID', 'Space Name'])

            # Format modularity to two decimal places for a cleaner sheet name
            modularity_str = f"{modularity:.2f}"
            sheet_name = f'Communities_Mod_{modularity_str}'
            comm_df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Visualization function
    def create_community_node_colors(graph, communities):
        """Creates color list for nodes based on community membership."""
        colors = ["#D4FCB1", "#CDC5FC", "#FFC2C4", "#F2D140", "#BCC6C8",
                  "#FFB6C1", "#98FB98", "#DDA0DD", "#F0E68C", "#87CEEB"]
        node_colors = []
        for node in graph:
            for i, community in enumerate(communities):
                if node in community:
                    node_colors.append(colors[i % len(colors)])
                    break
        return node_colors

    def visualize_communities(graph, communities, node_details, k):
        """Creates visualization for a specific community division."""
        node_colors = create_community_node_colors(graph, communities)
        modularity = round(nx.community.modularity(graph, communities), 6)

        plt.figure(figsize=(15, 10))
        plt.title(f"Community Visualization ({len(communities)} communities)\nModularity: {modularity}")

        # Create node labels using space names
        node_labels = {node: node_details.get(node, {}).get('Space Long Name', node)
                       for node in graph.nodes()}

        # Calculate layout
        pos = nx.spring_layout(graph, k=1, iterations=50)

        # Draw the graph
        nx.draw(graph, pos=pos,
                node_color=node_colors,
                node_size=1000,
                with_labels=True,
                labels=node_labels,
                font_size=8,
                font_color="black")

        # Save the plot
        plt.savefig(os.path.join(output_folder, f"{graph_name}_communities_{len(communities)}.png"),
                    bbox_inches='tight',
                    dpi=300)
        plt.close()

        # Add colors as node attributes to the graph
        for node, color in zip(graph.nodes(), node_colors):
            graph.nodes[node]['color'] = color  # Assigning color to the node attribute

        # Save community division as a .dot file
        dot_file_path = os.path.join(output_folder, f"{graph_name}_communities_{len(communities)}.dot")
        write_dot(graph, dot_file_path)
        print(f"Community division .dot file saved to: {dot_file_path}")

    # Create visualizations for different numbers of communities
    for k in range(min(15, len(communities))):  # Visualize first 3 divisions
        visualize_communities(graph, communities[k], node_details, k)

    # Plot modularity trend
    plt.figure(figsize=(10, 6))
    plt.plot(modularity_df['Community Split Index'],
             modularity_df['Modularity'],
             marker='o')
    plt.title('Modularity Trend for Girvan-Newman Community Detection')
    plt.xlabel('Community Split Index')
    plt.ylabel('Modularity')
    plt.grid(True)
    plt.savefig(os.path.join(output_folder, f"{graph_name}_modularity_trend.png"),
                bbox_inches='tight',
                dpi=300)
    plt.close()

    print(f"\nAnalysis complete:")
    print(f"Excel file saved to: {excel_path}")
    print(f"Visualizations saved to: {output_folder}")
    print(f"Total community divisions analyzed: {len(communities)}")


if __name__ == "__main__":
    # Your existing graph loading code
    # Search for the JSON file ending with "_space_combined_dict.json"
    search_pattern = os.path.join(output_dir, '*_space_info_dict.json')
    json_files = glob.glob(search_pattern)

    # Check if any such files were found
    if len(json_files) == 0:
        raise FileNotFoundError(f"No JSON file ending with '_space_combined_dict.json' found in directory {output_dir}")

    # Select the first matching file (you can modify this if you expect multiple and want different handling)
    dict_file_path = json_files[0]

    # dict_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC20-Office-Building_Output\AC20-Office-Building_space_combined_dict.json'  # change this
    # Load the JSON files into dictionaries
    # with open(dict_file_path) as f:
    #     space_info_dict = json.load(f)
    # json_file = space_info_dict
    # json_file = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC9R1-Haus-G-H-Ver2-2x3_Output\AC9R1-Haus-G-H-Ver2-2x3_space_info_dict.json'
    # dot_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC9R1-Haus-G-H-Ver2-2x3_Output\adjacent_rooms_graph_Spatial Proximity Graph - House_Obergeschoss.dot'
    # output_folder = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC9R1-Haus-G-H-Ver2-2x3_Output\Community Analysis'
    #
    # json_file = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC20-Office-Building_Output\AC20-Office-Building_space_info_dict.json'
    # dot_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC20-Office-Building_Output\adjacent_rooms_graph_Spatial Proximity Graph - Office Building_Erdgeschoss.dot'
    # output_folder = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC20-Office-Building_Output\Community Analysis'
    #
    # json_file = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Output\NBU_MedicalClinic_Arch_space_info_dict.json'
    # dot_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Output\adjacent_rooms_graph_Spatial Proximity Graph - Clinic without IA_First Floor.dot'
    # output_folder = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Output\Community Analysis'
    #
    # # json_file = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Output\NBU_MedicalClinic_Arch_space_info_dict.json'
    # # dot_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Output\Sub-Community Analysis\adjacent_rooms_graph_Spatial Proximity Graph - Medical Clinic_First Floor_community_id_2_without_indirect_edges.dot'
    # # output_folder = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Output\Sub-Community Analysis'
    #
    # json_file = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Door_Modified_Output\considering Direct Accessibiltiy\NBU_MedicalClinic_Arch_Door_Modified_space_info_dict.json'
    # dot_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Door_Modified_Output\considering Direct Accessibiltiy\adjacent_rooms_graph_Spatial Proximity Graph - Clinic without IA_First Floor.dot'
    # output_folder = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Output\Community Analysis'

    # Load the graph
    graph = nx.drawing.nx_pydot.read_dot(dot_file_path)

    # Remove dashed edges if needed
    edges_to_remove = [(u, v) for u, v, data in graph.edges(data=True)
                       if data.get('style') == 'dashed']
    # graph.remove_edges_from(edges_to_remove)

    # Extract graph name
    graph_name = os.path.splitext(os.path.basename(dot_file_path))[0]

    # Run community analysis
    analyze_communities(graph, json_file, cd_output_folder, graph_name)