import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.placement
import ifcopenshell.util.shape
from .ifc_element import IfcElement
from .ifc_project import IfcProject
import numpy as np

class IfcStair(IfcElement):
    def __init__(self, element):
        super().__init__(element)

    # def get_bounding_box_data(self):
    #     global_vertices = self.get_global_vertices(self.ifc_element)
    #     min_coords = np.min(global_vertices, axis=0)
    #     max_coords = np.max(global_vertices, axis=0)
    #
    #     return {
    #         'StairName': self.Name,
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

#
# if __name__ == "__main__":
#     # Load the IFC file
#     file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\models\AC20-Office-Building.ifc'
#     # file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\models\TUM_Gebaude N6_IFC4.ifc'
#     model = ifcopenshell.open(file_path)
#
#     # Get all stair and space elements in the model
#     stairs = model.by_type("IfcStair")
#     spaces = model.by_type("IfcSpace")
#
#     # Calculate bounding box data for all stairs and spaces
#     stair_bounding_boxes = [IfcElement(stair).get_bounding_box_data() for stair in stairs]
#     space_bounding_boxes = [IfcElement(space).get_bounding_box_data() for space in spaces]
#
#     # Dictionary to store overlapping information
#     overlap_dict = {}
#
#
#     def bounding_boxes_overlap(bb1, bb2):
#         return (bb1['MinX'] <= bb2['MaxX'] and bb1['MaxX'] >= bb2['MinX'] and
#                 bb1['MinY'] <= bb2['MaxY'] and bb1['MaxY'] >= bb2['MinY'] and
#                 bb1['MinZ'] <= bb2['MaxZ'] and bb1['MaxZ'] >= bb2['MinZ'])
#
#     # Check for overlaps and populate the dictionary
#     for stair_bb in stair_bounding_boxes:
#         overlapping_spaces = []
#         for space_bb in space_bounding_boxes:
#             if bounding_boxes_overlap(stair_bb, space_bb):
#                 overlapping_spaces.append(space_bb['Name'])
#         if overlapping_spaces:
#             overlap_dict[stair_bb['Name']] = overlapping_spaces
#
#     # Print the overlap dictionary
#     print(overlap_dict)