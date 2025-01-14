import ifcopenshell
import ifcopenshell.util.placement
import ifcopenshell.geom
import numpy as np


class IfcProject:
    def __init__(self, file_path):
        self.ifc_file = ifcopenshell.open(file_path)
        self.schema = self.ifc_file.schema
        self.by_id = self.ifc_file.by_id
        self.walls = self._get_elements_by_type("IfcWall")
        self.doors = self._get_elements_by_type("IfcDoor")

    def _get_elements_by_type(self, ifc_type):
        return self.ifc_file.by_type(ifc_type)

    def get_connects_path_elements(self):
        return self.ifc_file.by_type("IfcRelConnectsPathElements")

    def get_fills_elements(self):
        return self.ifc_file.by_type("IfcRelFillsElement")

    def get_voids_elements(self):
        return self.ifc_file.by_type("IfcRelVoidsElement")

    def get_coordinates(self, local_placement):
        if local_placement and local_placement.RelativePlacement:
            placement = local_placement.RelativePlacement
            if placement.is_a("IfcAxis2Placement3D"):
                return placement.Location.Coordinates
        return None

    def get_wall_coordinates(self, wall):
        if wall.ObjectPlacement:
            return self.get_coordinates(wall.ObjectPlacement)
        return None

    def get_door_coordinates(self, door):
        if door.ObjectPlacement:
            return self.get_coordinates(door.ObjectPlacement)
        return None

    def calculate_distance(self, coord1, coord2):
        return np.linalg.norm(np.array(coord1) - np.array(coord2))

    def get_element_coordinates(self, element):
        """Get the local placement coordinates of an IFC element."""
        if element.ObjectPlacement:
            matrix = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
            return matrix[:, 3][:3].tolist()
        return None

    def get_wall_start_end_coordinates(self, wall):
        """Get the start and end coordinates of a wall with same z-coordinate."""
        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), wall)
        vertices = shape.geometry.verts
        # Assuming the wall is represented by a polyline, we take the first and last vertex
        start_coord = vertices[0:3]
        end_coord = vertices[-3:]
        return start_coord, end_coord