import ifcopenshell.geom
import ifcopenshell.util.shape
from .ifc_element import IfcElement
import numpy as np

class IfcWall(IfcElement):
    def __init__(self, element):
        super().__init__(element)

    def calculate_bounding_box(self):
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, self.ifc_element)
        geometry = shape.geometry
        vertices = self.get_vertices(geometry)
        bbox = self.get_bbox(vertices)
        return bbox

    def get_transformation_matrix(self):
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, self.ifc_element)
        return ifcopenshell.util.shape.get_shape_matrix(shape)

    def get_bounding_box_data(self):
        min_coords, max_coords = self.calculate_bounding_box()
        minx, miny, minz = min_coords
        maxx, maxy, maxz = max_coords
        length_x = maxx - minx
        width_y = maxy - miny

        matrix = self.get_transformation_matrix()

        # Extract the translation part (last column, excluding the last row)
        translation_vector = matrix[:3, 3]

        # Extract the rotation part (upper-left 3x3 submatrix)
        rotation_matrix = matrix[:3, :3]

        # The local X-axis direction
        x_axis = rotation_matrix[:, 0]

        # Calculate the second point using the computed length
        second_point = translation_vector + length_x * x_axis

        # Calculate the midpoint
        midpoint = (translation_vector + second_point) / 2

        return {
            'Name': self.ifc_element.Name if hasattr(self.ifc_element, 'Name') else '',
            'GUID': self.ifc_element.GlobalId if hasattr(self.ifc_element, 'GlobalId') else '',
            'Length': length_x,
            'Width': width_y,
            'Start_Point': translation_vector.tolist(),
            'Mid_Point': midpoint.tolist(),
            'End_Point': second_point.tolist(),
            'Building_Storey': self.get_container_name()
        }