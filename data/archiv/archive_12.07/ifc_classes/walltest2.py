import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import ifcopenshell.util.element
from ifcopenshell.util.placement import get_local_placement
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Load the IFC file
file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
# file_path = r'C:\Users\harsh\Documents\Master Thesis\TUM_Gebaude N6_IFC4.ifc'
model = ifcopenshell.open(file_path)

# Get all walls in the model
walls = model.by_type('IfcWall')

# Function to compute the bounding box of vertices
def get_bbox(vertices):
    vertices = np.array(vertices)
    min_coords = np.min(vertices, axis=0)
    max_coords = np.max(vertices, axis=0)
    return min_coords, max_coords

# Initialize a list to store the results
wall_data = []

# Process each wall
for wall in walls:
    # Get the wall's name
    wall_name = wall.Name

    # Get the wall's geometric representation
    settings = ifcopenshell.geom.settings()
    shape = ifcopenshell.geom.create_shape(settings, wall)
    geometry = shape.geometry

    # Get the vertices of the wall
    vertices = ifcopenshell.util.shape.get_vertices(geometry)

    # Calculate the bounding box of the wall
    min_coords, max_coords = get_bbox(vertices)

    # Extract individual min and max values for x, y, z
    minx, miny, minz = min_coords
    maxx, maxy, maxz = max_coords

    # Calculate dimensions
    length_x = maxx - minx

    # Get the local placement of the wall
    placement = wall.ObjectPlacement
    transformation_matrix = get_local_placement(placement)

    # Extract the rotation part (upper-left 3x3 submatrix)
    rotation_matrix = transformation_matrix[:3, :3]

    # Extract the translation part (last column, excluding the last row)
    translation_vector = transformation_matrix[:3, 3]

    # The local X-axis direction
    x_axis = rotation_matrix[:, 0]

    # Calculate the second point using the computed length
    second_point = translation_vector + length_x * x_axis

    # Calculate the midpoint
    midpoint = (translation_vector + second_point) / 2

    # Store the results
    wall_data.append({
        'Wall Name': wall_name,
        'Origin': translation_vector,
        'Second Point': second_point,
        'Midpoint': midpoint
    })



# Convert the results to a pandas DataFrame
print(wall_data)
df = pd.DataFrame(wall_data)

# Prepare the Plotly figure
fig = go.Figure()

# Add lines and points for each wall
for index, row in df.iterrows():
    origin = row['Origin']
    second_point = row['Second Point']
    midpoint = row['Midpoint']
    wall_name = row['Wall Name']

    # Add the line between origin and second point
    fig.add_trace(go.Scatter3d(
        x=[origin[0], second_point[0]],
        y=[origin[1], second_point[1]],
        z=[origin[2], second_point[2]],
        mode='lines',
        name=wall_name,
        line=dict(width=5)
    ))

    # Add points at the origin and second point
    fig.add_trace(go.Scatter3d(
        x=[origin[0]],
        y=[origin[1]],
        z=[origin[2]],
        mode='markers',
        name=wall_name,
        marker=dict(size=5, color='blue')
    ))

    fig.add_trace(go.Scatter3d(
        x=[second_point[0]],
        y=[second_point[1]],
        z=[second_point[2]],
        mode='markers',
        name=wall_name,
        marker=dict(size=5, color='red')
    ))

    # Add the wall name at the midpoint
    fig.add_trace(go.Scatter3d(
        x=[midpoint[0]],
        y=[midpoint[1]],
        z=[midpoint[2]],
        mode='text',
        text=[wall_name],
        textposition="top center"
    ))

# Update the layout of the figure
fig.update_layout(
    title='Walls in 3D Space',
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    ),
    showlegend=False
)

# Show the figure
fig.show()
