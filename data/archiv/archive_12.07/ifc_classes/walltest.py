import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import ifcopenshell.util.element
import numpy as np
import pandas as pd
import plotly.express as px

def get_vertices(geometry):
    return ifcopenshell.util.shape.get_vertices(geometry)

def get_bbox(vertices):
    vertices = np.array(vertices)
    min_coords = np.min(vertices, axis=0)
    max_coords = np.max(vertices, axis=0)
    return min_coords, max_coords

def get_storey_elevation(file, element):
    container = ifcopenshell.util.element.get_container(element)
    while container:
        if container.is_a('IfcBuildingStorey'):
            return container.Elevation
        container = ifcopenshell.util.element.get_container(container)
    return None

def get_bbox_local(file, entity_type):
    settings = ifcopenshell.geom.settings()
    elements = file.by_type(entity_type)

    bboxes = []

    for element in elements:
        shape = ifcopenshell.geom.create_shape(settings, element)
        geometry = shape.geometry
        vertices = get_vertices(geometry)
        bbox = get_bbox(vertices)
        min_coords, max_coords = bbox

        # Extract individual min and max values for x, y, z
        minx, miny, minz = min_coords
        maxx, maxy, maxz = max_coords

        # Calculate dimensions
        length_x = maxx - minx
        width_y = maxy - miny

        # Extract the transformation matrix and location
        matrix = ifcopenshell.util.shape.get_shape_matrix(shape)
        location = matrix[:, 3][:3].tolist()  # Extract the location coordinates as list


        # Find the spatial container of an element
        container = ifcopenshell.util.element.get_container(element)
        container_name = container.Name if container else 'Unknown'

        # Get the elevation of the building storey
        elevation = get_storey_elevation(file, element)

        # Store bounding box data
        bboxes.append({
            'Name': element.Name if hasattr(element, 'Name') else '',
            'GUID': element.GlobalId if hasattr(element, 'GlobalId') else '',
            'Length_X': length_x,
            'Width_Y': width_y,
            'Location_X': location[0],  # Extract X coordinate
            'Location_Y': location[1],  # Extract Y coordinate
            'Location_Z': location[2],  # Extract Z coordinate
            'Building_storey': container_name,
            'Elevation': elevation
        })

    return bboxes

def main(ifc_file_path):
    # Open the IFC file
    ifc_file = ifcopenshell.open(ifc_file_path)

    # Get bounding boxes of all walls
    wall_bboxes = get_bbox_local(ifc_file, 'IfcWall')

    # Create a DataFrame to store bounding box data
    df = pd.DataFrame(wall_bboxes)

    # Print the DataFrame
    print(df)

    # Optionally, save the DataFrame to a CSV file
    df.to_csv('wall_bounding_boxes.csv', index=False)

    # Plot locations of walls using Plotly
    fig = px.scatter_3d(df, x='Location_X', y='Location_Y', z='Location_Z', text='Name', title='Locations of Walls')
    fig.update_traces(marker=dict(size=5))
    fig.show()

if __name__ == '__main__':
    file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
    main(file_path)
