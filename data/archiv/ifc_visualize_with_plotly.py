# things to add here
# dropdown for navigating between floors and whole model

import pandas as pd
import plotly.graph_objects as go

# Load the data from the CSV file
file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\AC20-FZK-Haus_wall_info.csv'
# file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output\TUM_Gebaude N6_IFC4_wall_info.csv'
data = pd.read_csv(file_path)

# Convert string representation of lists to actual lists
data['Start_Point'] = data['Start_Point'].apply(lambda x: eval(x))
data['Mid_Point'] = data['Mid_Point'].apply(lambda x: eval(x))
data['End_Point'] = data['End_Point'].apply(lambda x: eval(x))

# Extract coordinates
x_start = [point[0] for point in data['Start_Point']]
y_start = [point[1] for point in data['Start_Point']]
z_start = [point[2] for point in data['Start_Point']]

x_end = [point[0] for point in data['End_Point']]
y_end = [point[1] for point in data['End_Point']]
z_end = [point[2] for point in data['End_Point']]

# Create a 3D plot
fig = go.Figure()

# Add walls to the plot
for i in range(len(data)):
    fig.add_trace(go.Scatter3d(
        x=[x_start[i], x_end[i]],
        y=[y_start[i], y_end[i]],
        z=[z_start[i], z_end[i]],
        mode='lines',
        name=data['Name'][i]
    ))

# Update layout
fig.update_layout(
    title='Wall Plot',
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    )
)

# Show the plot
fig.show()
