import json
import glob
from collections import defaultdict
import networkx as nx
import os
import shutil
import subprocess
import pydot
from config import ifc_file_path, output_dir, graph_name

class IfcGraph(nx.Graph):
    def __init__(self, combined_dictionary=None, graph_name=None):
        self.adjacent_spaces_dict = combined_dictionary
        self.graph_name = graph_name

        # This is a color list for the building stories
        self.color_list = ["#808B96", "#e99d4e", "#a6cee3", "#b2df8a", "#fddbd0", "#91998e"]  # Last is default

        # Initialize space_storey_dict based on Space GlobalId
        self.space_storey_dict = {}
        if combined_dictionary:
            for space_id, space_data in combined_dictionary.items():
                self.space_storey_dict[space_id] = space_data["Space Storey"]["Storey Name"]

        super().__init__()
    def _sanitize_name(self, name):
        """
        Sanitizes the node or edge name by ensuring it does not contain invalid characters
        and truncates it to a maximum of 15 characters.
        """
        # Remove or replace any invalid characters (e.g., ":")
        sanitized_name = name.replace(":", "_")

        # Truncate the name to 15 characters if it exceeds that length
        if len(sanitized_name) > 15:
            sanitized_name = sanitized_name[:15]

        return sanitized_name

    def generate(self, save_dir=None, include_indirect_accessibility=False, include_exit_doors=False):
        graph_node_attribute_dict = {}

        # Create a mapping of story names to indices
        unique_stories = list(set(self.space_storey_dict.values()))
        story_to_color_index = {story: idx for idx, story in enumerate(unique_stories)}

        # Loop through each space in the dictionary
        for space_id, space_data in self.adjacent_spaces_dict.items():

            # Add edges for "Directly Accessible Spaces" (solid line)
            for direct_space in space_data.get("Directly Accessible Spaces", []):
                target_space_id = direct_space["Space GlobalId"]
                self.add_edge(space_id, target_space_id, style='solid')

            # Conditionally add edges for "Indirectly Accessible Spaces" (dashed line)
            if include_indirect_accessibility:
                for indirect_space in space_data.get("Indirectly Accessible Spaces", []):
                    target_space_id = indirect_space["Space GlobalId"]
                    self.add_edge(space_id, target_space_id, style='dashed')

            # Add edges for "Stair Accessible Spaces" (solid red line)
            for stair_space in space_data.get("Stair Accessible Spaces", []):
                target_space_id = stair_space["Space GlobalId"]
                self.add_edge(space_id, target_space_id, style='solid', color='red')

            # Add nodes to the graph
            self.add_node(space_id, label=space_data["Space Long Name"])

        # Conditionally add Exit Door nodes and edges
        if include_exit_doors:
            for space_id, space_data in self.adjacent_spaces_dict.items():
                exit_doors = space_data.get("Exit Door", [])
                for exit_door in exit_doors:
                    door_id = exit_door["Door GlobalId"]
                    door_name = self._sanitize_name(exit_door["Door Name"])

                    # Add edge between space and exit door (green line)
                    self.add_edge(space_id, door_id, style='solid', color='green')

                    # Add exit door node (square shape)
                    self.add_node(door_id, label=door_name, shape='square')

        # Calculate dynamic font sizes and edge widths based on node degree
        min_fontsize = 35
        max_fontsize = 35

        min_width = 1
        max_width = 4

        degree_list = [self.degree(node) for node in self.nodes]
        min_deg = min(degree_list)
        max_deg = max(degree_list)

        a_fontsize = (max_fontsize - min_fontsize) / (max_deg - min_deg) if max_deg > min_deg else 0
        b_fontsize = max_fontsize - a_fontsize * max_deg

        a_width = (max_width - min_width) / (max_deg - min_deg) if max_deg > min_deg else 0
        b_width = max_width - a_width * max_deg

        # Set node attributes dynamically
        for node in self.nodes:
            deg = self.degree(node)
            # Skip dynamic adjustments for exit doors (default size and width)
            if self.nodes[node].get('shape') == 'square':
                fontsize = min_fontsize  # Default size for exit door
                width = min_width  # Default width for exit door
            else:
                fontsize = a_fontsize * deg + b_fontsize
                width = a_width * deg + b_width

            # Get the story index (color index) based on Space GlobalId
            story_name = self.space_storey_dict.get(node, None)
            if story_name is not None:
                story_idx = story_to_color_index.get(story_name, len(self.color_list) - 1)
            else:
                story_idx = len(self.color_list) - 1

            if node not in graph_node_attribute_dict:
                graph_node_attribute_dict[node] = {"fontsize": fontsize, "width": width, "height": width,
                                                   "color": self.color_list[story_idx]}
            else:
                graph_node_attribute_dict[node]["fontsize"] = fontsize
                graph_node_attribute_dict[node]["width"] = width
                graph_node_attribute_dict[node]["height"] = width
                graph_node_attribute_dict[node]["color"] = self.color_list[story_idx]

        # Apply the node attributes to the graph
        nx.set_node_attributes(self, graph_node_attribute_dict)
        nx.set_node_attributes(self, values="Helvetica", name="fontname")
        nx.set_edge_attributes(self, values=5, name="penwidth")

        if save_dir is None:
            file_name = "adjacent_rooms_graph_" + self.graph_name
        else:
            file_name = os.path.join(save_dir, "adjacent_rooms_graph_" + self.graph_name)

        nx.drawing.nx_pydot.write_dot(self, file_name + ".dot")

        # If Python can't find the dot executable, change "app_path" variable to the full path
        app_path = shutil.which("dot")
        args = [app_path,
                "-Tpng",
                "-Ksfdp",
                "-Nstyle=filled",
                "-Nfixedsize=true",
                "-Grankdir=LR",
                "-Goverlap=scale",
                "-Gsplines=true",
                "-Gmargin=0",
                "-Gratio=fill",
                "-Gsize=7,5!",
                "-Gpack=true",
                "-Gdpi=1000",
                "-Grepulsiveforce=10",
                "-o" + file_name + ".png",
                file_name + ".dot"]

        subprocess.run(args=args)

        cwd = os.getcwd()
        # print("Generated graph can be found in directory: \"" + cwd + "\"")

    def generate_graph_for_each_storey(self, save_dir=None, include_indirect_accessibility=False,
                                       include_exit_doors=False):
        """Generate separate graphs and .dot files for each storey, optionally including indirect accessibility and exit doors."""
        unique_storeys = set(self.space_storey_dict.values())

        for storey in unique_storeys:
            # Filter spaces by storey
            filtered_spaces = {space_id: space_data for space_id, space_data in self.adjacent_spaces_dict.items()
                               if self.space_storey_dict[space_id] == storey}

            if not filtered_spaces:
                continue  # Skip if no spaces in this storey

            # Create a new graph for the current storey
            storey_graph = nx.Graph()
            graph_node_attribute_dict = {}

            # Add nodes and edges (excluding stair accessible spaces)
            for space_id, space_data in filtered_spaces.items():

                # Add edges for "Directly Accessible Spaces" (solid line)
                for direct_space in space_data.get("Directly Accessible Spaces", []):
                    target_space_id = direct_space["Space GlobalId"]
                    storey_graph.add_edge(space_id, target_space_id, style='solid')

                # Conditionally add Indirectly Accessible Spaces (dashed line)
                if include_indirect_accessibility:
                    for indirect_space in space_data.get("Indirectly Accessible Spaces", []):
                        target_space_id = indirect_space["Space GlobalId"]
                        storey_graph.add_edge(space_id, target_space_id, style='dashed')

                # Add nodes to the graph
                storey_graph.add_node(space_id, label=space_data["Space Long Name"])

                # Conditionally add Exit Door nodes and edges
                if include_exit_doors:
                    exit_doors = space_data.get("Exit Door", [])
                    for exit_door in exit_doors:
                        door_id = exit_door["Door GlobalId"]
                        door_name = self._sanitize_name(exit_door["Door Name"])

                        # Add edge between space and exit door (green line)
                        storey_graph.add_edge(space_id, door_id, style='solid', color='green')

                        # Add exit door node (square shape)
                        storey_graph.add_node(door_id, label=door_name, shape='square')

            # Calculate dynamic font sizes and edge widths based on node degree
            min_fontsize = 10
            max_fontsize = 35

            min_width = 1
            max_width = 4

            degree_list = [storey_graph.degree(node) for node in storey_graph.nodes]
            min_deg = min(degree_list)
            max_deg = max(degree_list)

            a_fontsize = (max_fontsize - min_fontsize) / (max_deg - min_deg) if max_deg > min_deg else 0
            b_fontsize = max_fontsize - a_fontsize * max_deg

            a_width = (max_width - min_width) / (max_deg - min_deg) if max_deg > min_deg else 0
            b_width = max_width - a_width * max_deg

            # Set node attributes dynamically
            for node in storey_graph.nodes:
                deg = storey_graph.degree(node)
                fontsize = a_fontsize * deg + b_fontsize
                width = a_width * deg + b_width

                # Get the story index (color index) based on Space GlobalId
                story_idx = self.color_list.index("#fddbd0")  # Default color in case no match is found
                if storey in self.color_list:
                    story_idx = self.color_list.index(storey)

                # Set node attributes (fontsize, width, height, color)
                graph_node_attribute_dict[node] = {
                    "fontsize": fontsize,
                    "width": width,
                    "height": width,
                    "color": self.color_list[story_idx]
                }

            # Apply the node attributes to the storey graph
            nx.set_node_attributes(storey_graph, graph_node_attribute_dict)
            nx.set_node_attributes(storey_graph, values="Helvetica", name="fontname")
            nx.set_edge_attributes(storey_graph, values=5, name="penwidth")

            # Save the graph to a .dot file and generate a PNG image for the storey
            if save_dir is None:
                file_name = "adjacent_rooms_graph_" + self.graph_name + "_" + storey
            else:
                file_name = os.path.join(save_dir, "adjacent_rooms_graph_" + self.graph_name + "_" + storey)

            # Save the .dot file
            nx.drawing.nx_pydot.write_dot(storey_graph, file_name + ".dot")

            # If Python can't find the dot executable, change "app_path" variable to the full path
            app_path = shutil.which("dot")
            args = [app_path,
                    "-Tpng",
                    "-Ksfdp",
                    "-Nstyle=filled",
                    "-Nfixedsize=true",
                    "-Grankdir=LR",
                    "-Goverlap=scale",
                    "-Gsplines=true",
                    "-Gmargin=0",
                    "-Gratio=fill",
                    "-Gsize=7,5!",
                    "-Gpack=true",
                    "-Gdpi=1000",
                    "-Grepulsiveforce=10",
                    "-o" + file_name + ".png",
                    file_name + ".dot"]

            subprocess.run(args=args)


if __name__ == "__main__":
    # Search for the JSON file ending with "_space_combined_dict.json"
    search_pattern = os.path.join(output_dir, '*_space_combined_dict.json')
    json_files = glob.glob(search_pattern)

    # Check if any such files were found
    if len(json_files) == 0:
        raise FileNotFoundError(f"No JSON file ending with '_space_combined_dict.json' found in directory {output_dir}")

    # Select the first matching file (you can modify this if you expect multiple and want different handling)
    dict_file_path = json_files[0]

    # dict_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC20-Office-Building_Output\AC20-Office-Building_space_combined_dict.json'  # change this
    # Load the JSON files into dictionaries
    with open(dict_file_path) as f:
        space_info_dict = json.load(f)
    combined_dict = space_info_dict



    ifc_graph = IfcGraph(combined_dictionary=combined_dict,
                         graph_name="Spatial Proximity Graph - Office Building")  # change this
    ifc_graph = IfcGraph(combined_dictionary=combined_dict, graph_name=graph_name)    #change this
    savedir = os.path.dirname(dict_file_path)
    ifc_graph.generate(save_dir=savedir, include_indirect_accessibility=False, include_exit_doors=True)
    ifc_graph.generate_graph_for_each_storey(save_dir=savedir, include_indirect_accessibility=True, include_exit_doors=True)