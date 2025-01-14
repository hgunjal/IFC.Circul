import ifcopenshell

def find_connecting_walls_for_all(ifc_file_path):
    # Open the IFC file
    ifc_file = ifcopenshell.open(ifc_file_path)

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
        connecting_walls_dict[wall] = connecting_walls

    return connecting_walls_dict

# Example usage:
if __name__ == '__main__':
    # Specify the file path to your IFC file
    file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
    connecting_walls_info = find_connecting_walls_for_all(file_path)

    # Print connecting walls for each wall
    for wall, connecting_walls in connecting_walls_info.items():
        print("Connecting walls for wall with ID {}: ".format(wall.id()))
        if connecting_walls:
            for connecting_wall in connecting_walls:
                print("- Wall ID: {}, Name: {}".format(connecting_wall.id(), connecting_wall.Name))
        else:
            print("No connecting walls found.")
