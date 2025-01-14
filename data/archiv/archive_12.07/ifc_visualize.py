import os
import json
import plotly.graph_objects as go
from ifc_classes.ifc_project import IfcProject


def plot_walls_and_doors_3d(ifc_project):
    fig = go.Figure()

    # Plot walls
    for wall in ifc_project.walls:
        start_coord, end_coord = ifc_project.get_wall_start_end_coordinates(wall)
        name = wall.Name if hasattr(wall, 'Name') else "Unnamed Wall"
        if start_coord and end_coord:
            fig.add_trace(go.Scatter3d(
                x=[start_coord[0], end_coord[0]],
                y=[start_coord[1], end_coord[1]],
                z=[start_coord[2], end_coord[2]],
                mode='lines+text',
                text=[name, name],
                line=dict(color='red'),
                name='Wall'
            ))

    # Plot doors
    for door in ifc_project.doors:
        coord = ifc_project.get_element_coordinates(door)
        name = door.Name if hasattr(door, 'Name') else "Unnamed Door"
        if coord:
            fig.add_trace(go.Scatter3d(
                x=[coord[0]],
                y=[coord[1]],
                z=[coord[2]],
                mode='markers+text',
                text=name,
                marker=dict(size=5, color='blue'),
                name='Door'
            ))

    fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'), title='Walls and Doors')
    fig.show()


def collect_coordinates(ifc_project):
    coordinates = {
        "walls": [],
        "doors": []
    }

    for wall in ifc_project.walls:
        start_coord, end_coord = ifc_project.get_wall_start_end_coordinates(wall)
        name = wall.Name if hasattr(wall, 'Name') else "Unnamed Wall"
        if start_coord and end_coord:
            coordinates["walls"].append({
                "id": wall.GlobalId,
                "name": name,
                "start_coordinates": start_coord,
                "end_coordinates": end_coord
            })

    for door in ifc_project.doors:
        coord = ifc_project.get_element_coordinates(door)
        name = door.Name if hasattr(door, 'Name') else "Unnamed Door"
        if coord:
            coordinates["doors"].append({
                "id": door.GlobalId,
                "name": name,
                "coordinates": coord
            })

    return coordinates


def save_coordinates_to_json(coordinates, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(coordinates, json_file, indent=4)


def main(ifc_file_path):
    if not os.path.exists(ifc_file_path):
        print(f"File not found: {ifc_file_path}")
        return

    try:
        ifc_project = IfcProject(ifc_file_path)

        # Plot walls and doors in 3D
        plot_walls_and_doors_3d(ifc_project)

        # Collect coordinates
        coordinates = collect_coordinates(ifc_project)

        # Save coordinates to JSON file
        json_file_path = os.path.splitext(ifc_file_path)[0] + '_coordinates.json'
        save_coordinates_to_json(coordinates, json_file_path)
        print(f"Coordinates saved to {json_file_path}")

    except OSError as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
    main(file_path)
