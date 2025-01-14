import json
import os
import ifcopenshell
from collections import defaultdict
from data.ifc_classes.ifc_project import IfcProject
from data.config import ifc_file_path
def find_exit_doors(space_door_mapping):
    door_connections = defaultdict(list)
    door_names = {}

    for space_guid, doors in space_door_mapping.items():
        if isinstance(doors, list):
            for door in doors:
                if isinstance(door, dict):
                    door_guid = door.get('Element GlobalID')
                    door_name = door.get('Element Name', 'Unknown')
                elif isinstance(door, str):
                    door_guid = door
                    door_name = 'Unknown'
                else:
                    continue

                if door_guid:
                    door_connections[door_guid].append(space_guid)
                    door_names[door_guid] = door_name
        elif isinstance(doors, str):
            door_guid = doors
            door_connections[door_guid].append(space_guid)
            door_names[door_guid] = 'Unknown'

    external_doors = {}
    for door_guid, connected_spaces in door_connections.items():
        if len(connected_spaces) == 1:
            external_doors[door_guid] = {
                'space_guid': connected_spaces[0],
                'name': door_names[door_guid]
            }

    return external_doors


def get_boundary_properties(space1_id, space2_id, ifc_file):
    """
    Check if two spaces share a virtual internal boundary.
    Returns True if they share a boundary that is both VIRTUAL and INTERNAL.
    """
    space1 = ifc_file.by_guid(space1_id)
    space2 = ifc_file.by_guid(space2_id)

    if not (space1 and space2):
        return False

    # Get boundaries for both spaces
    boundaries1 = space1.BoundedBy if hasattr(space1, 'BoundedBy') else []
    boundaries2 = space2.BoundedBy if hasattr(space2, 'BoundedBy') else []

    # Check each boundary combination
    for b1 in boundaries1:
        for b2 in boundaries2:
            if (b1.RelatedBuildingElement == b2.RelatedBuildingElement and
                    hasattr(b1, 'PhysicalOrVirtualBoundary') and
                    hasattr(b1, 'InternalOrExternalBoundary')):
                if (b1.PhysicalOrVirtualBoundary == 'VIRTUAL' and
                        b1.InternalOrExternalBoundary == 'INTERNAL'):
                    return True
    return False
def load_json(file_path):
    """Helper function to load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)


def create_combined_dictionary(
        space_info_dict,
        space_door_mapping,
        space_ve_mapping,
        space_wall_mapping,
        space_opening_mapping,
        space_to_stair_mapping,
        space_to_space_mapping,
        ifc_file_path,
        output_dir
):
    """
    Creates a combined dictionary from individual dictionaries and saves it to a JSON file.
    Now includes checks for virtual internal boundaries between spaces.
    """
    # Initialize combined dictionary
    combined_dict = {}

    # Load IFC file
    ifc_file = ifcopenshell.open(ifc_file_path)

    # Find exit doors
    exit_doors = find_exit_doors(space_door_mapping)

    # Build stair to spaces mapping
    stair_to_spaces = defaultdict(set)
    for space_id, stair_info_list in space_to_stair_mapping.items():
        for stair_info in stair_info_list:
            stair_global_id = stair_info["Element GlobalID"]
            stair_to_spaces[stair_global_id].add(space_id)

    # Process each space
    for space_id, space_details in space_info_dict.items():
        combined_dict[space_id] = space_details
        directly_accessible_spaces = []
        indirectly_accessible_spaces = []
        stair_accessible_spaces = []
        exit_door_list = []

        # Process adjacent spaces
        if space_id in space_to_space_mapping:
            for adjacent_space_id in space_to_space_mapping[space_id]:
                if adjacent_space_id not in space_info_dict:
                    continue

                # Initially add to indirectly accessible
                adjacent_space = {"Space GlobalId": adjacent_space_id}
                indirectly_accessible_spaces.append(adjacent_space)

                # Check for direct accessibility conditions
                is_directly_accessible = False

                # Check door connections
                if space_id in space_door_mapping and adjacent_space_id in space_door_mapping:
                    space_doors = space_door_mapping[space_id]
                    adjacent_doors = space_door_mapping[adjacent_space_id]
                    if any(door in adjacent_doors for door in space_doors):
                        is_directly_accessible = True

                # Check virtual element connections
                if not is_directly_accessible and space_id in space_ve_mapping and adjacent_space_id in space_ve_mapping:
                    space_ves = space_ve_mapping[space_id]
                    adjacent_ves = space_ve_mapping[adjacent_space_id]
                    if any(ve in adjacent_ves for ve in space_ves):
                        is_directly_accessible = True

                # # Check for virtual internal boundary
                # if not is_directly_accessible:
                #     if get_boundary_properties(space_id, adjacent_space_id, ifc_file):
                #         is_directly_accessible = True

                # Move to directly accessible if conditions are met
                if is_directly_accessible:
                    indirectly_accessible_spaces.remove(adjacent_space)
                    directly_accessible_spaces.append(adjacent_space)

        # Process stair connections
        if space_id in space_to_stair_mapping:
            for stair_info in space_to_stair_mapping[space_id]:
                stair_global_id = stair_info["Element GlobalID"]
                for connected_space_id in stair_to_spaces[stair_global_id]:
                    if connected_space_id != space_id:
                        stair_accessible = {"Space GlobalId": connected_space_id}
                        if stair_accessible not in stair_accessible_spaces:
                            stair_accessible_spaces.append(stair_accessible)

        # Process exit doors
        if space_id in space_door_mapping:
            doors = space_door_mapping[space_id]
            if isinstance(doors, list):
                for door in doors:
                    door_guid = door.get('Element GlobalID') if isinstance(door, dict) else door
                    if door_guid in exit_doors:
                        exit_door_list.append({
                            "Door GlobalId": door_guid,
                            "Door Name": exit_doors[door_guid]['name']
                        })
            elif isinstance(doors, str) and doors in exit_doors:
                exit_door_list.append({
                    "Door GlobalId": doors,
                    "Door Name": exit_doors[doors]['name']
                })

        # Update the combined dictionary
        combined_dict[space_id].update({
            "Directly Accessible Spaces": directly_accessible_spaces,
            "Indirectly Accessible Spaces": indirectly_accessible_spaces,
            "Stair Accessible Spaces": stair_accessible_spaces,
            "Exit Door": exit_door_list
        })

    # Save to file
    model_name = os.path.splitext(os.path.basename(ifc_file_path))[0]
    output_json_path = os.path.join(output_dir, f"{model_name}_space_combined_dict.json")

    with open(output_json_path, 'w') as json_file:
        json.dump(combined_dict, json_file, indent=4)

    print(f"Successfully exported combined dictionary to {output_json_path}")
# Example usage
if __name__ == "__main__":
    # Define file paths for your output
    output_dir = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Door_Modified_Output\considering Direct Accessibiltiy'
    output_json_path = os.path.join(output_dir, f"NBU_MedicalClinic_Arch_Door_Modified_space_combined_dict.json")

    input_dir = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\NBU_MedicalClinic_Arch_Door_Modified_Output\considering Direct Accessibiltiy'

    space_info_path = os.path.join(input_dir, 'NBU_MedicalClinic_Arch_Door_Modified_space_info_dict.json')
    space_door_path = os.path.join(input_dir, 'NBU_MedicalClinic_Arch_Door_Modified_space_door_relation.json')
    space_ve_path = os.path.join(input_dir, 'NBU_MedicalClinic_Arch_Door_Modified_space_ve_relation.json')
    space_wall_path = os.path.join(input_dir, 'NBU_MedicalClinic_Arch_Door_Modified_space_wall_relation.json')
    space_opening_path = os.path.join(input_dir, 'NBU_MedicalClinic_Arch_Door_Modified_space_opening_relation.json')
    space_stair_path = os.path.join(input_dir, 'NBU_MedicalClinic_Arch_Door_Modified_space_stair_relation.json')
    space_adjacent_path = os.path.join(input_dir, 'NBU_MedicalClinic_Arch_Door_Modified_adjacent_space_relation.json')

    # Load the data from each JSON file
    space_info_dict = load_json(space_info_path)
    space_door_mapping = load_json(space_door_path)
    space_ve_mapping = load_json(space_ve_path)
    space_wall_mapping = load_json(space_wall_path)
    space_opening_mapping = load_json(space_opening_path)
    space_to_stair_mapping = load_json(space_stair_path)
    space_to_space_mapping = load_json(space_adjacent_path)

    # Create the combined dictionary
    create_combined_dictionary(
        space_info_dict,
        space_door_mapping,
        space_ve_mapping,
        space_wall_mapping,
        space_opening_mapping,
        space_to_stair_mapping,
        space_to_space_mapping,
        ifc_file_path,
        output_dir
    )
