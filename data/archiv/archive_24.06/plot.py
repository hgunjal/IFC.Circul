import ifcopenshell
import networkx as nx
import matplotlib.pyplot as plt

def find_all_walls(ifc_file):
    """Retrieve all IfcWall instances."""
    return ifc_file.by_type("IfcWall")

def find_connecting_walls(ifc_file, walls):
    """Find connecting walls for all walls."""
    connects_path_elements = ifc_file.by_type("IfcRelConnectsPathElements")
    connecting_walls_dict = {}
    for wall in walls:
        connecting_walls = []
        for rel_connects in connects_path_elements:
            if rel_connects.RelatingElement.id() == wall.id():
                related_element_id = rel_connects.RelatedElement.id()
                related_wall = ifc_file.by_id(related_element_id)
                if related_wall is not None and related_wall.is_a("IfcWall"):
                    connecting_walls.append(related_wall)
        connecting_walls_dict[wall.id()] = connecting_walls
    return connecting_walls_dict

def find_doors_hosted_by_walls(ifc_file, walls):
    """Find doors hosted by walls."""
    doors = ifc_file.by_type("IfcDoor")
    fills_elements = ifc_file.by_type("IfcRelFillsElement")
    voids_elements = ifc_file.by_type("IfcRelVoidsElement")

    door_hosting_dict = {}
    for wall in walls:
        wall_id = wall.id()
        door_hosting_dict[wall_id] = []

    for door in doors:
        fills_voids_rel = next((rel for rel in fills_elements if rel.RelatedBuildingElement == door), None)
        if fills_voids_rel:
            opening_element = fills_voids_rel.RelatingOpeningElement
            voids_element_rel = next((rel for rel in voids_elements if rel.RelatedOpeningElement == opening_element), None)
            if voids_element_rel:
                host_wall = voids_element_rel.RelatingBuildingElement
                host_wall_id = host_wall.id()
                if host_wall_id in door_hosting_dict:
                    door_hosting_dict[host_wall_id].append(door)
    return door_hosting_dict

def plot_network_graph(walls, connecting_walls_dict, door_hosting_dict, internal_walls, external_walls):
    """Plot the network graph."""
    G = nx.Graph()

    # Add wall nodes
    for wall in walls:
        wall_id = wall.id()
        wall_name = wall.Name

        # Determine the color and shape based on whether the wall is internal or external
        if wall_name in internal_walls:
            node_color = 'green'  # Internal walls
            node_shape = 'o'
        elif wall_name in external_walls:
            node_color = 'red'  # External walls
            node_shape = 's'
        else:
            continue

        G.add_node(wall_id, label=f"Wall: {wall_name}", color=node_color, shape=node_shape)

        # Add connecting walls
        connecting_walls = connecting_walls_dict.get(wall_id, [])
        for connecting_wall in connecting_walls:
            connecting_wall_id = connecting_wall.id()
            connecting_wall_name = connecting_wall.Name
            if connecting_wall_name in internal_walls:
                connect_node_color = 'green'
                connect_node_shape = 's'
            elif connecting_wall_name in external_walls:
                connect_node_color = 'red'
                connect_node_shape = 's'
            else:
                continue

            G.add_node(connecting_wall_id, label=f"Wall: {connecting_wall_name}", color=connect_node_color, shape=connect_node_shape)
            G.add_edge(wall_id, connecting_wall_id, label="connects to", style='solid')

        # Add doors hosted by the wall
        doors = door_hosting_dict.get(wall_id, [])
        for door in doors:
            door_id = door.id()
            door_name = door.Name
            G.add_node(door_id, label=f"Door: {door_name}", color='yellow', shape='o')
            G.add_edge(wall_id, door_id, label="hosts", style='dashed')

    # Plot the graph
    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'label')
    colors = [G.nodes[node]['color'] for node in G.nodes]
    shapes = set((G.nodes[node]['shape'] for node in G.nodes))

    plt.figure(figsize=(12, 8))

    for shape in shapes:
        nx.draw_networkx_nodes(G, pos, nodelist=[node for node in G.nodes if G.nodes[node]['shape'] == shape],
                               node_color=[G.nodes[node]['color'] for node in G.nodes if G.nodes[node]['shape'] == shape],
                               node_shape=shape, node_size=3000, label=shape)
        
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_color='black', font_weight='bold')

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.show()

def main(ifc_file_path):
    """Main function to execute the workflow."""
    ifc_file = ifcopenshell.open(ifc_file_path)

    # Workflow steps
    walls = find_all_walls(ifc_file)
    connecting_walls_dict = find_connecting_walls(ifc_file, walls)
    door_hosting_dict = find_doors_hosted_by_walls(ifc_file, walls)

    # Define internal and external walls
    internal_walls = [
        "Wand-Int-ERDG-4",
        "Wand-Int-ERDG-2",
        "Wand-Int-ERDG-1",
        "Wand-Int-ERDG-3",
        "Wand-Int-ERDG-5"
    ]

    external_walls = [
        "Wand-Ext-ERDG-1",
        "Wand-Ext-ERDG-4",
        "Wand-Ext-ERDG-3",
        "Wand-Ext-ERDG-2",
    ]

    # Plot the network graph
    plot_network_graph(walls, connecting_walls_dict, door_hosting_dict, internal_walls, external_walls)

if __name__ == '__main__':
    file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
    main(file_path)
