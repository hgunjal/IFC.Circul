import ifcopenshell
from ifc_classes.ifc_project import IfcProject
from ifc_classes.ifc_wall import IfcWall
from ifc_classes.ifc_door import IfcDoor  # Ensure IfcDoor is imported
import numpy as np
import ifcopenshell.geom
class IfcAnalysis:
    def __init__(self, ifc_project):
        self.ifc_project = ifc_project
        self.walls = {wall.id(): IfcWall(wall) for wall in ifc_project.walls}
        self.doors = {door.id(): IfcDoor(door) for door in ifc_project.doors}
        self.door_host_wall_dict = self.find_host_walls_for_doors()

    def find_host_walls_for_doors(self):
        # Retrieve all IfcDoor instances
        doors = self.ifc_project.doors

        # Retrieve all IfcRelFillsElement and IfcRelVoidsElement relationships
        fills_elements = self.ifc_project.get_fills_elements()
        voids_elements = self.ifc_project.get_voids_elements()

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

    def analyze_walls_and_openings(self):
        if self.walls:
            for wall_id, wall_obj in self.walls.items():
                wall = wall_obj.wall
                if wall.GlobalId in self.door_host_wall_dict.values():
                    print(f"Wall Name: {wall.Name}")
                    print(f"Wall GlobalId: {wall.GlobalId}")

                    # Retrieve all IfcOpeningElement instances within the wall
                    openings = wall.HasOpenings
                    if openings:
                        for opening_rel in openings:
                            if opening_rel.is_a("IfcRelVoidsElement"):
                                opening_element = opening_rel.RelatedOpeningElement

                                # Check if the opening element is in the door_host_wall_dict
                                if opening_element.GlobalId in self.door_host_wall_dict:
                                    # print(f"  Opening Element GlobalId: {opening_element.GlobalId}")

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
                                                    print(f"    Coordinates for Opening '{opening_element.Name}': {coordinates}")
                                                elif relative_placement.is_a("IfcAxis2Placement2D"):
                                                    coordinates = relative_placement.Location.Coordinates
                                                    print(f"    Coordinates of IfcLocalPlacement for Opening '{opening_element.Name}': {coordinates} (2D placement)")
                                                else:
                                                    print("    Unknown placement type")
                                            else:
                                                print("    No RelativePlacement found")
                                        else:
                                            print("    ObjectPlacement is not IfcLocalPlacement")
                                    else:
                                        print("    No ObjectPlacement found for Opening")


# Example usage:
def main(ifc_file_path):
    ifc_project = IfcProject(ifc_file_path)
    analysis = IfcAnalysis(ifc_project)
    analysis.analyze_walls_and_openings()

    # doors = ifc_project.doors
    # for d in doors:
    #     print(f"Door GlobalId: {d.GlobalId}, Name: {d.Name}") #get all doors

if __name__ == '__main__':
    file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
    # file_path = r'C:\Users\harsh\Documents\Master Thesis\TUM_Gebaude N6_IFC4.ifc'
    main(file_path)