import ifcopenshell

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
            voids_element_rel = next((rel for rel in voids_elements if rel.RelatedOpeningElement == opening_element), None)

            if voids_element_rel:
                host_wall = voids_element_rel.RelatingBuildingElement
                door_host_wall_dict[opening_element.GlobalId] = host_wall.GlobalId

    return door_host_wall_dict

# Specify the file path to your IFC file
file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'

# Get the dictionary of opening elements related to doors and their host walls
door_host_wall_dict = find_host_walls_for_doors(file_path)

# Open the IFC model
model = ifcopenshell.open(file_path)

# Get all IfcWall entities from the model
walls = model.by_type("IfcWall")

if walls:
    for wall in walls:
        if wall.GlobalId in door_host_wall_dict.values():
            print(f"Wall Name: {wall.Name}")
            print(f"Wall GlobalId: {wall.GlobalId}")

            # Retrieve all IfcOpeningElement instances within the wall
            openings = wall.HasOpenings
            if openings:
                for opening_rel in openings:
                    if opening_rel.is_a("IfcRelVoidsElement"):
                        opening_element = opening_rel.RelatedOpeningElement

                        # Check if the opening element is in the door_host_wall_dict
                        if opening_element.GlobalId in door_host_wall_dict:
                            print(f"  Opening Element GlobalId: {opening_element.GlobalId}")

                            # Retrieve the ObjectPlacement associated with the opening element
                            object_placement = opening_element.ObjectPlacement
                            if object_placement:
                                if object_placement.is_a("IfcLocalPlacement"):
                                    local_placement = object_placement

                                    # Check the RelativePlacement
                                    relative_placement = local_placement.RelativePlacement
                                    if relative_placement:
                                        if relative_placement.is_a("IfcAxis2Placement3D"):
                                            coordinates = relative_placement.Location.Coordinates
                                            print(
                                                f"    Coordinates of IfcLocalPlacement for Opening '{opening_element.Name}': {coordinates}")
                                        elif relative_placement.is_a("IfcAxis2Placement2D"):
                                            coordinates = relative_placement.Location.Coordinates
                                            print(
                                                f"    Coordinates of IfcLocalPlacement for Opening '{opening_element.Name}': {coordinates} (2D placement)")
                                        else:
                                            print("    Unknown placement type")
                                    else:
                                        print("    No RelativePlacement found")
                                else:
                                    print("    ObjectPlacement is not IfcLocalPlacement")
                            else:
                                print("    No ObjectPlacement found for Opening")
            else:
                print("No openings found for Wall")
else:
    print("No IfcWall entities found in the model")
