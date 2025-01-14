import ifcopenshell.geom
import ifcopenshell.util.shape
from .ifc_element import IfcElement
from .ifc_project import IfcProject
import numpy as np


class IfcSpace(IfcElement):
    def __init__(self, element):
        super().__init__(element)
        self.LongName = element.LongName if hasattr(element,
                                                    'LongName') else None  # Long name of the space, if it exists

    # def get_bounding_box_data(self):
    #     global_vertices = self.get_global_vertices(self.ifc_element)
    #     min_coords = np.min(global_vertices, axis=0)
    #     max_coords = np.max(global_vertices, axis=0)
    #
    #     return {
    #         'SpaceName': self.Name,
    #         'MinX': min_coords[0],
    #         'MinY': min_coords[1],
    #         'MinZ': min_coords[2],
    #         'MaxX': max_coords[0],
    #         'MaxY': max_coords[1],
    #         'MaxZ': max_coords[2],
    #         'BBLength': max_coords[0] - min_coords[0],
    #         'BBWidth': max_coords[1] - min_coords[1],
    #         'BBHeight': max_coords[2] - min_coords[2],
    #     }

    def get_adjoining_walls_in_space(self):
        boundaries = []
        if hasattr(self.ifc_element, "BoundedBy"):
            for rel_space_boundary in self.ifc_element.BoundedBy:
                element = rel_space_boundary.RelatedBuildingElement
                if element and element.is_a("IfcWall"):
                    wall_info = self.get_ifc_rel_space_boundary_info(rel_space_boundary)
                    if wall_info not in boundaries:  # Avoid appending duplicates
                        boundaries.append(wall_info)
        # If no IfcRelSpaceBoundary relationships are found, append a placeholder message
        if not boundaries:
            boundaries.append("No IfcRelSpaceBoundary relationships.")
        return boundaries

    def get_adjoining_doors_in_space(self):
        boundaries = []
        if hasattr(self.ifc_element, "BoundedBy"):
            for rel_space_boundary in self.ifc_element.BoundedBy:
                element = rel_space_boundary.RelatedBuildingElement
                if element and element.is_a("IfcDoor"):
                    door_info = self.get_ifc_rel_space_boundary_info(rel_space_boundary)
                    if door_info not in boundaries:  # Avoid appending duplicates
                        boundaries.append(door_info)
        # If no IfcRelSpaceBoundary relationships are found, append a placeholder message
        if not boundaries:
            boundaries.append("No IfcRelSpaceBoundary relationships.")
        return boundaries

    def get_adjoining_ve_in_space(self):        #ve = IfcVirtualElement
        boundaries = []
        if hasattr(self.ifc_element, "BoundedBy"):
            for rel_space_boundary in self.ifc_element.BoundedBy:
                element = rel_space_boundary.RelatedBuildingElement
                if element and element.is_a("IfcVirtualElement"):
                    ve_info = self.get_ifc_rel_space_boundary_info(rel_space_boundary)
                    if ve_info not in boundaries:  # Avoid appending duplicates
                        boundaries.append(ve_info)
        # # If no IfcRelSpaceBoundary relationships are found, append a placeholder message
        # if not boundaries:
        #     boundaries.append("No IfcRelSpaceBoundary relationships.")
        return boundaries

    def get_adjoining_openings_in_space(self):
        boundaries = []
        if hasattr(self.ifc_element, "BoundedBy"):
            for rel_space_boundary in self.ifc_element.BoundedBy:
                element = rel_space_boundary.RelatedBuildingElement
                if element and element.is_a("IfcOpeningElement"):
                    opening_info = self.get_ifc_rel_space_boundary_info(rel_space_boundary)
                    if opening_info not in boundaries:  # Avoid appending duplicates
                        boundaries.append(opening_info)
        # If no IfcRelSpaceBoundary relationships are found, append a placeholder message
        if not boundaries:
            boundaries.append("No IfcRelSpaceBoundary relationships.")
        return boundaries

    @staticmethod
    def get_ifc_rel_space_boundary_info(rel_space_boundary):
        info = {
            "Element Name": rel_space_boundary.RelatedBuildingElement.Name if rel_space_boundary.RelatedBuildingElement else None,
            "Element GlobalID": rel_space_boundary.RelatedBuildingElement.GlobalId if rel_space_boundary.RelatedBuildingElement else None,
        }
        return info

    def get_storey_name_and_elevation(self):
        """
        Retrieves the name and elevation of the IfcBuildingStorey associated with the given IfcSpace.
        """
        # Step 1: Retrieve all `IfcRelAggregates` relationships where this `IfcSpace` is the `RelatedObjects`
        for rel in self.ifc_element.Decomposes:
            if rel.is_a('IfcRelAggregates'):
                container = rel.RelatingObject
                if container.is_a('IfcBuildingStorey'):
                    # print(f"Found IfcBuildingStorey: {container.Name}, Elevation: {container.Elevation}")  # Debugging
                    return {
                        'Storey Name': container.Name,
                        'Storey Elevation': container.Elevation
                    }

        print("No IfcBuildingStorey found.")  # Debugging: when no storey is found
        return {
            'StoreyName': 'Unknown',
            'StoreyElevation': None
        }

    def to_dict(self):
        """
        Create a dictionary with the structure:
        Key = IfcSpace(s).GlobalId
        Value = {
            "Element Name": IfcSpace(s).Name,
            "Element Long Name": IfcSpace(s).LongName
        }
        """
        return {
            self.GlobalId: {
                "Space Name": self.Name,
                "Space Long Name": self.LongName,
                "Space Storey": self.get_storey_name_and_elevation()
            }
        }

if __name__ == "__main__":
    ifc_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\models\AC20-FZK-Haus.ifc'
    model = IfcProject(ifc_file_path)

    stairs = model.ifc_file.by_type("IfcSpace")

    # Initialize list to store bounding box data for each stair
    all_coords = []

    # Loop through all stairs and get their bounding box data
    for stair in stairs:
        stair_instance = IfcSpace(stair)
        bbdata = stair_instance.get_bounding_box_data()
        all_coords.append(bbdata)

    # Print the coordinates
    print(all_coords)