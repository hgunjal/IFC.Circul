import ifcopenshell
from ifc_classes.ifc_project import IfcProject
from ifc_classes.ifc_wall import IfcWall
from ifc_classes.ifc_door import IfcDoor  # Ensure IfcDoor is imported
import numpy as np
import ifcopenshell.geom

class IfcAnalysis:
    def __init__(self, ifc_project):
        self.ifc_project = ifc_project
        self.walls = {wall.id(): IfcWall(wall) for wall in ifc_project.get_all_walls()}
        self.doors = {door.id(): IfcDoor(door) for door in ifc_project.get_all_doors()}  # Initialize IfcDoor instances

    def find_walls_with_doors(self):
        fills_elements = self.ifc_project.get_fills_elements()
        voids_elements = self.ifc_project.get_voids_elements()

        walls_with_doors = {}

        for wall_id, wall_obj in self.walls.items():
            wall = wall_obj.wall

            # Retrieve all openings (IfcRelVoidsElement) associated with the wall
            openings = wall.HasOpenings
            if openings:
                for opening_rel in openings:
                    if opening_rel.is_a("IfcRelVoidsElement"):
                        opening_element = opening_rel.RelatedOpeningElement

                        # Check if the opening element is related to a door
                        fills_voids_rel = next(
                            (rel for rel in fills_elements if rel.RelatedBuildingElement == opening_element), None)
                        if fills_voids_rel:
                            relating_building_element = fills_voids_rel.RelatingBuildingElement
                            if relating_building_element.id() in self.doors:
                                door = self.doors[relating_building_element.id()]
                                if wall_id not in walls_with_doors:
                                    walls_with_doors[wall_id] = []
                                walls_with_doors[wall_id].append(door)

        return walls_with_doors

    def find_doors_hosted_by_walls(self):
        fills_elements = self.ifc_project.get_fills_elements()
        voids_elements = self.ifc_project.get_voids_elements()

        door_hosting_dict = {wall_id: [] for wall_id in self.walls.keys()}

        for door in self.doors.values():
            fills_voids_rel = next((rel for rel in fills_elements if rel.RelatedBuildingElement == door.door), None)
            if fills_voids_rel:
                opening_element = fills_voids_rel.RelatingOpeningElement
                voids_element_rel = next((rel for rel in voids_elements if rel.RelatedOpeningElement == opening_element), None)
                if voids_element_rel:
                    host_wall = voids_element_rel.RelatingBuildingElement
                    host_wall_id = host_wall.id()
                    if host_wall_id in door_hosting_dict:
                        door_hosting_dict[host_wall_id].append(door)
        return door_hosting_dict

    def extract_vertices(self, shape):
        vertices = shape.geometry.verts
        grouped_vertices = []
        for i in range(0, len(vertices), 3):
            grouped_vertices.append(vertices[i:i+3])
        return np.array(grouped_vertices)

    def calculate_distance_between_door_and_wall_start(self):
        door_hosting_dict = self.find_doors_hosted_by_walls()

        settings = ifcopenshell.geom.settings()
        for wall_id, doors in door_hosting_dict.items():
            wall = self.walls[wall_id]

            # Extract wall vertices
            wall_shape = ifcopenshell.geom.create_shape(settings, wall.wall)
            wall_verts = self.extract_vertices(wall_shape)


            # Print openings information
            if wall.openings:
                for opening in wall.openings:
                    opening_element = opening['element']
                    opening_vertices = opening['vertices']
                    print(f"Opening Element '{opening_element.Name}'; '{opening_element.is_a}' on Wall '{wall.name}'")
                    print(f"Opening Vertices:\n{opening_vertices}")

                    print(f"Checking opening element: {opening_element.Name} (GlobalId: {opening_element.GlobalId})")


            else:
                print(f"No openings found on Wall '{wall.name}'")

            for door in doors:
                middle_point = door.middle_point
                print("Perform other calculations as needed")

    def extract_opening_coordinates(self):
        fills_elements = self.ifc_project.get_fills_elements()
        voids_elements = self.ifc_project.get_voids_elements()

        for wall_id, wall_obj in self.walls.items():
            wall = wall_obj.wall  # Accessing the IfcWall object from IfcWall wrapper
            print(f"Wall GlobalId: {wall.GlobalId}")

            openings = wall.HasOpenings
            if openings:
                for opening_rel in openings:
                    if opening_rel.is_a("IfcRelVoidsElement"):
                        opening_element = opening_rel.RelatedOpeningElement
                        print(f"  Opening Element GlobalId: {opening_element.GlobalId}")

                        fills_voids_rel = next((rel for rel in fills_elements if rel.RelatedBuildingElement == opening_element), None)
                        if fills_voids_rel:
                            relating_building_element = fills_voids_rel.RelatingBuildingElement
                            print(f"    Relating Building Element GlobalId: {relating_building_element.GlobalId}")

                            # Determine if the opening element is a door
                            if relating_building_element.id() in self.doors:
                                door = self.doors[relating_building_element.id()]
                                print(f"    Opening is a door: {door.name} (GlobalId: {door.id})")
                            else:
                                print(f"    Opening is not a door")

                            object_placement = opening_element.ObjectPlacement
                            if object_placement and object_placement.is_a("IfcLocalPlacement"):
                                local_placement = object_placement
                                relative_placement = local_placement.RelativePlacement
                                if relative_placement:
                                    if relative_placement.is_a("IfcAxis2Placement3D"):
                                        coordinates = relative_placement.Location.Coordinates
                                        print(f"      Coordinates of IfcLocalPlacement: {coordinates}")
                                    elif relative_placement.is_a("IfcAxis2Placement2D"):
                                        coordinates = relative_placement.Location.Coordinates
                                        print(f"      Coordinates of IfcLocalPlacement: {coordinates} (2D placement)")
                                    else:
                                        print("      Unknown placement type")
                                else:
                                    print("      No RelativePlacement found")
                            else:
                                print("      No ObjectPlacement found for Opening")
                        else:
                            print("    No fills relationship found")
            else:
                print("No openings found for Wall")

    def perform_analysis(self):
        walls_with_doors = self.find_walls_with_doors()
        for wall_id, doors in walls_with_doors.items():
            wall = self.walls[wall_id]
            print(f"Wall '{wall.name}' (GlobalId: {wall.id()}) has the following doors:")
            for door in doors:
                print(f"  - Door '{door.name}' (GlobalId: {door.id})")
                extract_opening_coordinates()

def main(ifc_file_path):
    ifc_project = IfcProject(ifc_file_path)
    analysis = IfcAnalysis(ifc_project)
    analysis.extract_opening_coordinates()

if __name__ == '__main__':
    file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
    main(file_path)
