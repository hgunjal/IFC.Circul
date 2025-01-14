import ifcopenshell

def find_connecting_walls(ifc_file):
    # Retrieve all IfcWall instances
    walls = ifc_file.by_type("IfcWall")

    # Retrieve all IfcRelConnectsPathElements relationships
    connects_path_elements = ifc_file.by_type("IfcRelConnectsPathElements")

    # Dictionary to store connecting walls for each wall
    connecting_walls_dict = {}

    # Iterate over each wall
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


def find_host_walls_for_doors(ifc_file_path):
    # Open the IFC file
    ifc_file = ifcopenshell.open(ifc_file_path)

    # Retrieve all IfcDoor instances
    doors = ifc_file.by_type("IfcDoor")

    # Retrieve all IfcRelFillsElement and IfcRelVoidsElement relationships
    fills_elements = ifc_file.by_type("IfcRelFillsElement")
    voids_elements = ifc_file.by_type("IfcRelVoidsElement")

    # Dictionary to store door GlobalIds and their corresponding host wall GlobalIds
    door_host_wall_dict = {}

    # Iterate over each door
    for door in doors:
        # Find the IfcRelFillsElement relationship for the door
        fills_voids_rel = next((rel for rel in fills_elements if rel.RelatedBuildingElement == door), None)

        if fills_voids_rel:
            opening_element = fills_voids_rel.RelatingOpeningElement

            # Find the IfcRelVoidsElement relationship for the opening element
            voids_element_rel = next((rel for rel in voids_elements if rel.RelatedOpeningElement == opening_element),
                                     None)

            if voids_element_rel:
                host_wall = voids_element_rel.RelatingBuildingElement
                door_host_wall_dict[door.GlobalId] = host_wall.GlobalId

    return door_host_wall_dict


if __name__ == '__main__':
    # Specify the file path to your IFC file
    file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
    door_host_wall_dict = find_host_walls_for_doors(file_path)
    for door_id, wall_id in door_host_wall_dict.items():
        print(f"Door GlobalId: {door_id}, Host Wall GlobalId: {wall_id}")
