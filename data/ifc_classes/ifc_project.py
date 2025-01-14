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
        self.spaces = self._get_elements_by_type("IfcSpace")
        self.RelVoidsElement = self._get_elements_by_type("IfcRelVoidsElement")


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