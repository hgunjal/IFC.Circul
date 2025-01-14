import ifcopenshell

def find_host_walls_for_doors(ifc_file_path):
    # Open the IFC file
    ifc_file = ifcopenshell.open(ifc_file_path)

    # Retrieve all IfcDoor instances
    doors = ifc_file.by_type("IfcDoor")
    
    # Retrieve all IfcRelFillsElement and IfcRelVoidsElement relationships
    fills_elements = ifc_file.by_type("IfcRelFillsElement")
    voids_elements = ifc_file.by_type("IfcRelVoidsElement")

    # Iterate over each door
    for door in doors:
        print(f"Checking door: {door.Name} (GlobalId: {door.GlobalId})")

        # Find the IfcRelFillsElement relationship for the door
        fills_voids_rel = next((rel for rel in fills_elements if rel.RelatedBuildingElement == door), None)

        if fills_voids_rel:
            print(f" - Found IfcRelFillsElement (GlobalId: {fills_voids_rel.GlobalId})")
            opening_element = fills_voids_rel.RelatingOpeningElement
            print(f" - Opening Element: {opening_element.GlobalId}")

            # Find the IfcRelVoidsElement relationship for the opening element
            voids_element_rel = next((rel for rel in voids_elements if rel.RelatedOpeningElement == opening_element), None)

            if voids_element_rel:
                print(f" - Found IfcRelVoidsElement (GlobalId: {voids_element_rel.GlobalId})")
                host_wall = voids_element_rel.RelatingBuildingElement
                print(f"Door '{door.Name}' (GlobalId: {door.GlobalId}) is hosted by Wall '{host_wall.Name}' (GlobalId: {host_wall.GlobalId})")
            else:
                print(f"Door '{door.Name}' (GlobalId: {door.GlobalId}) is not hosted by a wall (no IfcRelVoidsElement found)")
        else:
            print(f"Door '{door.Name}' (GlobalId: {door.GlobalId}) does not have an opening element (no IfcRelFillsElement found)")

if __name__ == '__main__':
    # Specify the file path to your IFC file
    file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
    find_host_walls_for_doors(file_path)
