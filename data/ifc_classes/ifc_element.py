import ifcopenshell.util.shape
import ifcopenshell.util.placement
import ifcopenshell.util.element
import ifcopenshell.geom
# from ifc_project import IfcProject
from .ifc_project import IfcProject
import numpy as np
class IfcElement:
    def __init__(self, ifc_element):
        self.ifc_element = ifc_element
        self.id = ifc_element.id()
        self.Name = ifc_element.Name
        self.GlobalId = ifc_element.GlobalId

    @staticmethod
    def get_global_vertices(element):
        # Get the local placement of the element
        local_placement = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)

        # Get the vertices of the element
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, element)
        geometry = shape.geometry
        vertices = ifcopenshell.util.shape.get_vertices(geometry)

        # Transform the vertices to the global coordinate system
        global_vertices = []
        for vertex in vertices:
            local_vertex = np.append(vertex, 1)  # Make it a homogenous coordinate for transformation
            global_vertex = local_placement @ local_vertex  # Apply the transformation
            global_vertices.append(global_vertex[:3])  # Extract the x, y, z coordinates

        return np.array(global_vertices)

    def get_bounding_box_data(self):
        global_vertices = self.get_global_vertices(self.ifc_element)
        min_coords = np.min(global_vertices, axis=0)
        max_coords = np.max(global_vertices, axis=0)

        return {
            'GlobalId': self.GlobalId,
            'Name': self.Name,
            'MinX': min_coords[0],
            'MinY': min_coords[1],
            'MinZ': min_coords[2],
            'MaxX': max_coords[0],
            'MaxY': max_coords[1],
            'MaxZ': max_coords[2]
        }


    def get_local_placement(self):
        return ifcopenshell.util.placement.get_local_placement(self.ifc_element.ObjectPlacement)

    def get_storey_elevation(self):         #does not work for ifcspace
        container = ifcopenshell.util.element.get_container(self.ifc_element)
        while container:
            if container.is_a('IfcBuildingStorey'):
                return container.Elevation
            container = ifcopenshell.util.element.get_container(container)
        return None

    def get_container_name(self):
        container = ifcopenshell.util.element.get_container(self.ifc_element)
        return container.Name if container else 'Unknown'

    # New function to get the name and elevation of the building storey
    def get_storey_name_and_elevation(self):
        # Step 1: Retrieve all `IfcRelAggregates` relationships where this `IfcSpace` is the `RelatedObjects`
        for rel in self.ifc_element.Rel:
            if rel.is_a('IfcRelAggregates'):
                container = rel.RelatingObject
                if container.is_a('IfcBuildingStorey'):
                    print(f"Found IfcBuildingStorey: {container.Name}, Elevation: {container.Elevation}")  # Debugging
                    return {
                        'Storey Name': container.Name,
                        'Storey Elevation': container.Elevation
                    }

        print("No IfcBuildingStorey found.")  # Debugging: when no storey is found
        return {
            'StoreyName': 'Unknown',
            'StoreyElevation': None
        }


if __name__ == "__main__":
    ifc_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\models\Duplex_A_20110907_optimized.ifc'
    model = IfcProject(ifc_file_path)

    spaces = model.ifc_file.by_type("IfcStairFlight")

    # Initialize list to store bounding box data for each stair
    sd = []

    # Loop through all stairs and get their bounding box data
    for space in spaces:
        space_instance = IfcElement(space)
        storey_data = space_instance.get_bounding_box_data()
        sd.append(storey_data)

    # Print the coordinates
    print(sd)