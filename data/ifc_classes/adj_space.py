# misc non-standard libraries
import ifcopenshell
import ifcopenshell.geom
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
# custom
from data.utils.progressbar import progressbar

# standard
import math
import os
import numpy as np
import itertools
import json


class IfcGeometry:
    def __init__(self,
                 ifc_file_path=None,  # An open ifc-file
                 name=None,  # Name of the SpaceGeometryContainer
                 force_init=False,  # Force the creation of a new SpaceGeometryContainer object
                 exclude_space_list=[],  # List with names of rooms that should not be included
                 voxel_distance=0.5):  # Distance between grid voxels along each axis X, Y, Z

        self.ifc_file_path = ifc_file_path
        self.name = name
        self.force_init = force_init
        self.exclude_space_list = exclude_space_list
        self.voxel_distance = voxel_distance
        self.x_size = None
        self.y_size = None
        self.z_size = None
        self.voxel_x_location_vec = None
        self.voxel_y_location_vec = None
        self.voxel_z_location_vec = None
        self.grid_shape = None
        self.space_idx_dict = {}
        self.neutral_idx = -50
        self.ambient_idx = -100

        # This is a color list for the building stories
        self.color_list = ["#808B96", "#e99d4e", "#a6cee3", "#b2df8a", "#fddbd0", "#91998e"]  # Last is default

        self.init_geometry()
        self.init_3D_space_idx_array()

    def init_geometry(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        space_map_filename = current_dir + "/" + "space_map_" + self.name + ".pickle"
        if self.force_init or os.path.isfile(space_map_filename) == False:
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            id_iter = itertools.count()

            # print("Extracting geometry from ifc...")
            neutral_space_name = "Area"  # spaces that doesnt classify as a room but is a part of the building
            ifc_file = ifcopenshell.open(self.ifc_file_path)
            ifc_space_list = ifc_file.by_type("IfcSpace")
            ifc_storey_list = ifc_file.by_type("IfcBuildingStorey")

            if len(ifc_space_list) == 0:
                print("Ifc-file does not contain any space objects -> quitting...")
            else:
                self.space_name_list = []
                self.space_mesh_list = []
                self.space_type_name_dict = {}
                self.space_storey_dict = {}

                self.space_name_neutral_list = []
                self.space_mesh_neutral_list = []

                space_counter = 0
                for storey_counter, storey in enumerate(ifc_storey_list):
                    for ifc_rel_aggregates in storey.IsDecomposedBy:
                        for space in ifc_rel_aggregates.RelatedObjects:
                            shape = ifcopenshell.geom.create_shape(settings, space)
                            vertices = shape.geometry.verts
                            edges = shape.geometry.edges
                            faces = shape.geometry.faces

                            if space.Name is None:  # If the space has no name, give it a generic name
                                space.Name = "Space_" + str(next(id_iter))

                            grouped_vertices = np.array(
                                [[vertices[i], vertices[i + 1], vertices[i + 2]] for i in range(0, len(vertices), 3)])
                            grouped_edges = np.array([[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)])
                            grouped_faces = np.array(
                                [[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)])

                            mesh = trimesh.Trimesh(vertices=grouped_vertices,
                                                   faces=grouped_faces)

                            if (space.Name in self.exclude_space_list) == False:
                                if space.LongName == neutral_space_name:
                                    self.space_name_neutral_list.append(space.Name)
                                    self.space_mesh_neutral_list.append(mesh)
                                else:
                                    self.space_name_list.append(space.Name)
                                    self.space_mesh_list.append(mesh)
                                    self.space_type_name_dict[space.Name] = space.LongName
                                    self.space_storey_dict[space.Name] = storey_counter

                            # progressbar(space_counter, 0, len(ifc_space_list) - 1)
                            space_counter += 1

                # Check for duplicate room names
                if len(set(self.space_name_list)) != len(self.space_name_list):
                    print("Warning: duplicate space names found in IFC.")

    def init_3D_space_idx_array(self):
        min_x_list = []
        min_y_list = []
        min_z_list = []

        max_x_list = []
        max_y_list = []
        max_z_list = []

        for space_mesh in self.space_mesh_list:
            min_x_list.append(np.min(space_mesh.vertices[:, 0]))
            min_y_list.append(np.min(space_mesh.vertices[:, 1]))
            min_z_list.append(np.min(space_mesh.vertices[:, 2]))

            max_x_list.append(np.max(space_mesh.vertices[:, 0]))
            max_y_list.append(np.max(space_mesh.vertices[:, 1]))
            max_z_list.append(np.max(space_mesh.vertices[:, 2]))

        for space_mesh in self.space_mesh_neutral_list:
            min_x_list.append(np.min(space_mesh.vertices[:, 0]))
            min_y_list.append(np.min(space_mesh.vertices[:, 1]))
            min_z_list.append(np.min(space_mesh.vertices[:, 2]))

            max_x_list.append(np.max(space_mesh.vertices[:, 0]))
            max_y_list.append(np.max(space_mesh.vertices[:, 1]))
            max_z_list.append(np.max(space_mesh.vertices[:, 2]))

        min_x = np.min(np.array(min_x_list))
        min_y = np.min(np.array(min_y_list))
        min_z = np.min(np.array(min_z_list))

        max_x = np.max(np.array(max_x_list))
        max_y = np.max(np.array(max_y_list))
        max_z = np.max(np.array(max_z_list))

        self.x_size = math.floor((max_x - min_x) / self.voxel_distance) + 2
        self.y_size = math.floor((max_y - min_y) / self.voxel_distance) + 2
        self.z_size = math.floor((max_z - min_z) / self.voxel_distance) + 2

        x_rem = (max_x - min_x) - self.x_size * self.voxel_distance
        z_rem = (max_y - min_y) - self.y_size * self.voxel_distance
        y_rem = (max_z - min_z) - self.z_size * self.voxel_distance

        min_x = min_x + x_rem * 0.5 - self.voxel_distance  # add additional outdoor block
        min_y = min_y + y_rem * 0.5 - self.voxel_distance  # add additional outdoor block
        min_z = min_z + z_rem * 0.5 - self.voxel_distance  # add additional outdoor block

        max_x = max_x - x_rem * 0.5 + self.voxel_distance  # add additional outdoor block
        max_y = max_y - y_rem * 0.5 + self.voxel_distance  # add additional outdoor block
        max_z = max_z - z_rem * 0.5 + self.voxel_distance  # add additional outdoor block

        voxel_x_idx_vec = np.arange(self.x_size)  # (x_size)
        voxel_y_idx_vec = np.arange(self.y_size)  # (y_size)
        voxel_z_idx_vec = np.arange(self.z_size)  # (z_size)

        self.voxel_x_location_vec = np.linspace(min_x, max_x, self.x_size)  # (x_size) // location of voxel
        self.voxel_y_location_vec = np.linspace(min_y, max_y, self.y_size)  # (y_size)
        self.voxel_z_location_vec = np.linspace(min_z, max_z, self.z_size)  # (conv_z_size)

        voxel_x_idx_mesh, voxel_y_idx_mesh, voxel_z_idx_mesh = np.meshgrid(voxel_x_idx_vec, voxel_y_idx_vec,
                                                                           voxel_z_idx_vec)
        voxel_x_location_mesh, voxel_y_location_mesh, voxel_z_location_mesh = np.meshgrid(self.voxel_x_location_vec,
                                                                                          self.voxel_y_location_vec,
                                                                                          self.voxel_z_location_vec)

        idx_mesh = np.swapaxes(np.array([voxel_x_idx_mesh, voxel_y_idx_mesh, voxel_z_idx_mesh]), 0,
                               3)  # (conv_x_size,conv_y_size,conv_z_size,3)
        location_mesh = np.swapaxes(np.array([voxel_x_location_mesh, voxel_y_location_mesh, voxel_z_location_mesh]), 0,
                                    3)  # (conv_x_size,conv_y_size,conv_z_size)

        idx_mesh_vec = np.reshape(idx_mesh,
                                  (idx_mesh.shape[0] * idx_mesh.shape[1] * idx_mesh.shape[2], idx_mesh.shape[3]))
        location_mesh_vec = np.reshape(location_mesh, (
            location_mesh.shape[0] * location_mesh.shape[1] * location_mesh.shape[2], location_mesh.shape[3]))

        # print("Generating space to position index map...")
        self.grid_shape = (self.x_size, self.y_size, self.z_size)
        self._3D_space_idx_array = np.ones(self.grid_shape, dtype=np.int64) * self.ambient_idx

        # Set indices for neutral space
        for space_counter, space_mesh in enumerate(self.space_mesh_neutral_list):
            bool_vec = space_mesh.contains(location_mesh_vec)
            x_idx = idx_mesh_vec[bool_vec, 0]
            y_idx = idx_mesh_vec[bool_vec, 1]
            z_idx = idx_mesh_vec[bool_vec, 2]
            self._3D_space_idx_array[x_idx, y_idx, z_idx] = self.neutral_idx

            # progressbar(space_counter, 0, len(self.space_mesh_neutral_list) - 1)

        # Set indices for normal space
        for space_counter, space_mesh in enumerate(self.space_mesh_list):
            bool_vec = space_mesh.contains(location_mesh_vec)
            x_idx = idx_mesh_vec[bool_vec, 0]
            y_idx = idx_mesh_vec[bool_vec, 1]
            z_idx = idx_mesh_vec[bool_vec, 2]
            self._3D_space_idx_array[x_idx, y_idx, z_idx] = space_counter
            self.space_idx_dict[self.space_name_list[space_counter]] = space_counter

            # progressbar(space_counter, 0, len(self.space_mesh_list) - 1)

    def get_point_space_idx(self, x_idx, y_idx, z_idx):
        return self._3D_space_idx_array[x_idx, y_idx, z_idx]

    def get_adjacent_spaces_dict(self):
        x_bool = np.equal(self._3D_space_idx_array[:-1, :, :], self._3D_space_idx_array[1:, :, :]) == False
        y_bool = (self._3D_space_idx_array[:, :-1, :] == self._3D_space_idx_array[:, 1:, :]) == False
        z_bool = (self._3D_space_idx_array[:, :, :-1] == self._3D_space_idx_array[:, :, 1:]) == False

        dx_idx_space_1_x, dx_idx_space_1_y, dx_idx_space_1_z = np.where(x_bool)
        dy_idx_space_1_x, dy_idx_space_1_y, dy_idx_space_1_z = np.where(y_bool)
        dz_idx_space_1_x, dz_idx_space_1_y, dz_idx_space_1_z = np.where(z_bool)

        dx_idx_space_2_x = dx_idx_space_1_x + 1
        dy_idx_space_2_x = dy_idx_space_1_x
        dz_idx_space_2_x = dz_idx_space_1_x

        dx_idx_space_2_y = dx_idx_space_1_y
        dy_idx_space_2_y = dy_idx_space_1_y + 1
        dz_idx_space_2_y = dz_idx_space_1_y

        dx_idx_space_2_z = dx_idx_space_1_z
        dy_idx_space_2_z = dy_idx_space_1_z
        dz_idx_space_2_z = dz_idx_space_1_z + 1

        dx_idx_pair_1 = self._3D_space_idx_array[dx_idx_space_1_x, dx_idx_space_1_y, dx_idx_space_1_z]
        dx_idx_pair_2 = self._3D_space_idx_array[dx_idx_space_2_x, dx_idx_space_2_y, dx_idx_space_2_z]
        dy_idx_pair_1 = self._3D_space_idx_array[dy_idx_space_1_x, dy_idx_space_1_y, dy_idx_space_1_z]
        dy_idx_pair_2 = self._3D_space_idx_array[dy_idx_space_2_x, dy_idx_space_2_y, dy_idx_space_2_z]
        dz_idx_pair_1 = self._3D_space_idx_array[dz_idx_space_1_x, dz_idx_space_1_y, dz_idx_space_1_z]
        dz_idx_pair_2 = self._3D_space_idx_array[dz_idx_space_2_x, dz_idx_space_2_y, dz_idx_space_2_z]

        # For each point in the generated mesh, it is checked which space the adjacent point is encapsulated by.
        # If the adjacent point does not belong to a space, the subsequent point is checked.
        # This is done up until "n_search_blocks" away from the original point.
        n_search_blocks = 2
        for i in range(n_search_blocks):
            dx_temp = dx_idx_space_2_x + i + 1
            dx_temp[dx_temp >= self.grid_shape[0]] = dx_idx_space_2_x[dx_temp >= self.grid_shape[0]]
            temp = self._3D_space_idx_array[
                dx_temp, dx_idx_space_2_y, dx_idx_space_2_z]  ###     If +1 point is not a room then check +2 point
            bool_dx = np.logical_or(dx_idx_pair_2 == self.neutral_idx, dx_idx_pair_2 == self.ambient_idx)  ###
            dx_idx_pair_2[bool_dx] = temp[bool_dx]  ###

            dy_temp = dy_idx_space_2_y + i + 1
            dy_temp[dy_temp >= self.grid_shape[1]] = dy_idx_space_2_y[dy_temp >= self.grid_shape[1]]
            temp = self._3D_space_idx_array[dy_idx_space_2_x, dy_temp, dy_idx_space_2_z]  ###
            bool_dy = np.logical_or(dy_idx_pair_2 == self.neutral_idx, dy_idx_pair_2 == self.ambient_idx)  ###
            dy_idx_pair_2[bool_dy] = temp[bool_dy]  ###

            dz_temp = dz_idx_space_2_z + i + 1
            dz_temp[dz_temp >= self.grid_shape[2]] = dz_idx_space_2_z[dz_temp >= self.grid_shape[2]]
            temp = self._3D_space_idx_array[dz_idx_space_2_x, dz_idx_space_2_y, dz_temp]  ###
            bool_dz = np.logical_or(dz_idx_pair_2 == self.neutral_idx, dz_idx_pair_2 == self.ambient_idx)  ###
            dz_idx_pair_2[bool_dz] = temp[bool_dz]  ###

        dx_idx_pair = np.array([dx_idx_pair_1, dx_idx_pair_2])
        dy_idx_pair = np.array([dy_idx_pair_1, dy_idx_pair_2])
        dz_idx_pair = np.array([dz_idx_pair_1, dz_idx_pair_2])

        dx_pair_list = []
        while True:
            dx_pair_list.append(dx_idx_pair[:, 0])
            is_equal_bool = np.equal(dx_idx_pair[:, 0].reshape((2, 1)), dx_idx_pair)
            is_equal_bool = np.logical_and(is_equal_bool[0], is_equal_bool[1])
            if np.all(is_equal_bool):
                break
            else:
                dx_idx_pair = dx_idx_pair[:, is_equal_bool == False]

        dy_pair_list = []
        while True:
            dy_pair_list.append(dy_idx_pair[:, 0])
            is_equal_bool = np.equal(dy_idx_pair[:, 0].reshape((2, 1)), dy_idx_pair)
            is_equal_bool = np.logical_and(is_equal_bool[0], is_equal_bool[1])
            if np.all(is_equal_bool):
                break
            else:
                dy_idx_pair = dy_idx_pair[:, is_equal_bool == False]

        dz_pair_list = []
        while True:
            dz_pair_list.append(dz_idx_pair[:, 0])
            is_equal_bool = np.equal(dz_idx_pair[:, 0].reshape((2, 1)), dz_idx_pair)
            is_equal_bool = np.logical_and(is_equal_bool[0], is_equal_bool[1])
            if np.all(is_equal_bool):
                break
            else:
                dz_idx_pair = dz_idx_pair[:, is_equal_bool == False]

        pair_list = []
        pair_list.extend(dx_pair_list)
        pair_list.extend(dy_pair_list)
        pair_list.extend(dz_pair_list)
        pair_vec = np.array(pair_list).transpose()
        bool_no_self_reference = pair_vec[0, :] != pair_vec[1, :]
        pair_vec = pair_vec[:, bool_no_self_reference]
        pair_list_no_duplicates = []
        while True:
            pair_1 = pair_vec[:, 0]
            pair_2 = np.array([pair_vec[1, 0], pair_vec[0, 0]])
            pair_list_no_duplicates.append(pair_1)
            is_equal_bool_1 = np.equal(pair_1.reshape((2, 1)), pair_vec)
            is_equal_bool_1 = np.logical_and(is_equal_bool_1[0], is_equal_bool_1[1])
            is_equal_bool_2 = np.equal(pair_2.reshape((2, 1)), pair_vec)
            is_equal_bool_2 = np.logical_and(is_equal_bool_2[0], is_equal_bool_2[1])
            is_equal_bool = np.logical_or(is_equal_bool_1, is_equal_bool_2)
            if np.all(is_equal_bool):
                break
            else:
                pair_vec = pair_vec[:, is_equal_bool == False]

        adjacent_spaces_dict = {}
        pair_vec_no_duplicates = np.array(pair_list_no_duplicates).transpose()
        for space_counter, space_name in enumerate(self.space_name_list):
            bool_1 = space_counter == pair_vec_no_duplicates[0, :]
            bool_2 = space_counter == pair_vec_no_duplicates[1, :]
            idx_vec_1 = pair_vec_no_duplicates[1, bool_1]
            idx_vec_2 = pair_vec_no_duplicates[0, bool_2]
            adjacent_space_list = []
            for el in idx_vec_1:
                if el != -50 and el != -100:
                    adjacent_space_list.append(self.space_name_list[el])
            for el in idx_vec_2:
                if el != -50 and el != -100:
                    adjacent_space_list.append(self.space_name_list[el])
            adjacent_spaces_dict[space_name] = adjacent_space_list

        ####### IF duplicate space names occur in the IFC and these spaces are adjacent then the resulting adjacent_space_dict will have elements that reference themselves #########

        return adjacent_spaces_dict

    def get_space_type_name_dict(self):
        return self.space_type_name_dict

    def get_space_storey_dict(self):
        return self.space_storey_dict

    def visualize_plotly(self):
        # Create a list to hold the Plotly Mesh3d traces
        mesh_traces = []

        # Collect all point data for a possible point cloud visualization
        point_cloud = []

        # Loop through each mesh and create a Mesh3d object in Plotly
        for space_name, mesh in zip(self.space_name_list, self.space_mesh_list):
            # Get the color from the color list using the space-storey mapping
            color = self.color_list[self.space_storey_dict[space_name]]
            rgba_color = trimesh.visual.color.hex_to_rgba(color)

            # Normalize the RGBA color for Plotly (0-1 range)
            rgba_normalized = [c / 255 for c in rgba_color[:3]]
            opacity = rgba_color[3] / 255  # Use the alpha channel for opacity

            # Add the mesh's vertices to the point cloud
            point_cloud.extend(mesh.vertices)

            # Create the Mesh3d trace for the current mesh
            mesh_trace = go.Mesh3d(
                x=mesh.vertices[:, 0],
                y=mesh.vertices[:, 1],
                z=mesh.vertices[:, 2],
                i=mesh.faces[:, 0],
                j=mesh.faces[:, 1],
                k=mesh.faces[:, 2],
                color=f'rgba({rgba_normalized[0] * 255},{rgba_normalized[1] * 255},{rgba_normalized[2] * 255},{opacity})',
                opacity=opacity
            )
            mesh_traces.append(mesh_trace)

        # Create the 3D figure with all the mesh traces
        fig = go.Figure(data=mesh_traces)

        # Adjust the camera angles similar to your Trimesh setup
        camera = dict(
            eye=dict(
                x=np.sin(0.4 * np.pi) * np.cos(-0.25 * np.pi),
                y=np.sin(0.4 * np.pi) * np.sin(-0.25 * np.pi),
                z=np.cos(0.4 * np.pi)
            )
        )

        # Update the layout with the camera and other settings
        fig.update_layout(
            scene_camera=camera,
            scene=dict(
                xaxis=dict(title='X', showbackground=False),
                yaxis=dict(title='Y', showbackground=False),
                zaxis=dict(title='Z', showbackground=False),
            ),
            margin=dict(r=0, l=0, b=0, t=0),
            width=800,
            height=800
        )

        # Show the figure
        fig.show()

def filter_by_storey(dict1, dict2):
    dict3 = {}
    for key, adjacents in dict1.items():
        storey = dict2[key]
        filtered_adjacents = [adj for adj in adjacents if dict2[adj] == storey]
        if filtered_adjacents:  # Only add the key if there are filtered adjacents
            dict3[key] = filtered_adjacents
    return dict3


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def visualize_voxel_grid(ifc_geometry):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot voxels
    voxels = ifc_geometry._3D_space_idx_array != ifc_geometry.ambient_idx

    ax.voxels(voxels, facecolors='cyan', edgecolor='k')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.title('Voxel Grid Representation')
    plt.show()


import os
import numpy as np
import plotly.graph_objects as go


def visualize_voxel_grid_plotly(ifc_geometry):
    # Extract the voxel indices where space exists (not ambient)
    voxels = ifc_geometry._3D_space_idx_array != ifc_geometry.ambient_idx
    x, y, z = np.where(voxels)

    # Create a 3D plot using multiple cube traces
    cubes = []
    cube_size = 1  # Size of each cube (adjust to your grid spacing)

    # Iterate over each voxel and create a cube
    for xi, yi, zi in zip(x, y, z):
        # Coordinates of the corners of the cube
        cube_corners = [
            (xi, yi, zi),
            (xi + cube_size, yi, zi),
            (xi + cube_size, yi + cube_size, zi),
            (xi, yi + cube_size, zi),
            (xi, yi, zi + cube_size),
            (xi + cube_size, yi, zi + cube_size),
            (xi + cube_size, yi + cube_size, zi + cube_size),
            (xi, yi + cube_size, zi + cube_size)
        ]

        # Define the cube faces using the corners
        cube_faces = [
            [cube_corners[j] for j in [0, 1, 5, 4]],
            [cube_corners[j] for j in [1, 2, 6, 5]],
            [cube_corners[j] for j in [2, 3, 7, 6]],
            [cube_corners[j] for j in [3, 0, 4, 7]],
            [cube_corners[j] for j in [0, 1, 2, 3]],
            [cube_corners[j] for j in [4, 5, 6, 7]]
        ]

        # Add each face as a mesh trace
        for face in cube_faces:
            x_face, y_face, z_face = zip(*face)
            cubes.append(go.Mesh3d(
                x=x_face,
                y=y_face,
                z=z_face,
                color='blue',
                opacity=0.5
            ))

    # Create the figure
    fig = go.Figure(data=cubes)

    # Update layout for better visualization
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X', showbackground=False),
            yaxis=dict(title='Y', showbackground=False),
            zaxis=dict(title='Z', showbackground=False),
        ),
        margin=dict(r=0, l=0, b=0, t=0),
        width=800,
        height=800
    )

    fig.show()


def visualize_v_grid(ifc_geometry, save_dir=None, storey_filter=None):
    """
    Visualize voxel grid with distinct colors for each space, optionally filtered by IfcBuildingStorey.

    Parameters:
        ifc_geometry: Instance of IfcGeometry containing the voxel grid and space data.
        save_dir: Directory to save the images. If None, views will be displayed interactively.
        storey_filter: Filter to visualize voxels belonging to a specific IfcBuildingStorey. If None, plot all spaces.
    """
    # Create figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Get space indices for the specified storey or all spaces
    if storey_filter is not None:
        # Filter spaces by the storey
        filtered_space_indices = [
            space_idx for space_name, space_idx in ifc_geometry.space_idx_dict.items()
            if ifc_geometry.space_storey_dict.get(space_name) == storey_filter
        ]
    else:
        # Include all spaces
        filtered_space_indices = list(ifc_geometry.space_idx_dict.values())

    # Filter unique space indices (excluding ambient and neutral spaces)
    space_indices = np.array(filtered_space_indices)
    space_indices = space_indices[~np.isin(space_indices, [ifc_geometry.ambient_idx, ifc_geometry.neutral_idx])]

    # Create a colormap with distinct colors for each space
    import matplotlib.colors as mcolors
    colors = plt.cm.Set3(np.linspace(0, 1, len(space_indices)))

    # Create a color array the same shape as the voxel grid
    color_array = np.zeros((*ifc_geometry._3D_space_idx_array.shape, 4))

    # Assign colors to spaces
    for idx, space_idx in enumerate(space_indices):
        mask = (ifc_geometry._3D_space_idx_array == space_idx)
        color_array[mask] = colors[idx]

    # Handle neutral spaces (if any)
    neutral_mask = (ifc_geometry._3D_space_idx_array == ifc_geometry.neutral_idx)
    if np.any(neutral_mask):
        color_array[neutral_mask] = [0.8, 0.8, 0.8, 1.0]  # Gray color for neutral spaces

    # Create boolean array for where voxels should be plotted
    voxels = (ifc_geometry._3D_space_idx_array != ifc_geometry.ambient_idx) & (
        np.isin(ifc_geometry._3D_space_idx_array, space_indices)
    )

    # Plot colored voxels
    ax.voxels(voxels, facecolors=color_array, edgecolor='k', linewidth=0.5)

    # Add a color bar legend
    import matplotlib.patches as mpatches
    legend_patches = []
    for idx, space_idx in enumerate(space_indices):
        # Find the space name corresponding to this index
        space_name = None
        for name, index in ifc_geometry.space_idx_dict.items():
            if index == space_idx:
                space_name = name
                break
        if space_name:
            patch = mpatches.Patch(color=colors[idx], label=f'Space: {space_name}')
            legend_patches.append(patch)

    # Add neutral space to legend if it exists
    if np.any(neutral_mask):
        neutral_patch = mpatches.Patch(color=[0.8, 0.8, 0.8], label='Neutral Space')
        legend_patches.append(neutral_patch)

    # Place legend outside the plot
    ax.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left')

    # Define views with corresponding angles
    views = {
        "top": (90, 0),
        "bottom": (-90, 0),
        "front": (0, 0),
        "back": (0, 180),
        "left": (0, 90),
        "right": (0, -90)
    }

    # Loop through views to save or display them
    for view_name, (elev, azim) in views.items():
        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.title(
            f'Voxel Grid - {view_name.capitalize()} View (Storey: {storey_filter if storey_filter is not None else "All"})')

        if save_dir:
            # Ensure the save directory exists
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            # Add tight_layout to prevent legend cutoff
            plt.tight_layout()
            save_path = os.path.join(save_dir,
                                     f"voxel_grid_{view_name}_storey_{storey_filter if storey_filter is not None else 'all'}.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved {view_name} view to {save_path}")
        else:
            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    # Import time module
    import time

    # record start time
    start = time.time()

    ifc_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\models\Residential House.ifc'
    ifc_file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\models\NBU_MedicalClinic_Arch_Door_Modified.ifc'
    project_name = "test"
    model_name, _ = os.path.splitext(os.path.basename(ifc_file_path))
    ifc_geometry = IfcGeometry(ifc_file_path, project_name, force_init=False)
    adjacent_spaces_dict = ifc_geometry.get_adjacent_spaces_dict()
    space_idx_dict = ifc_geometry.space_idx_dict
    print(space_idx_dict)

    # record end time
    end = time.time()

    # print the difference between start
    # and end time in milli. secs
    print("The time of execution of above program is :",
          (end - start) * 10 ** 3, "ms")

    #visualize_v_grid(ifc_geometry, storey_filter=0) #save_dir=r"C:\Users\harsh\Documents\Master Thesis\Figures\House_Voxel_grids"


    # print(adjacent_spaces_dict)
    # visualize_voxel_grid(ifc_geometry)
    # ifc_geometry.visualize_plotly()

    # space_type_name_dict = ifc_geometry.get_space_type_name_dict()
    # print(space_type_name_dict)
    # space_storey_dict = ifc_geometry.get_space_storey_dict()
    # print(space_storey_dict)
    # space_adj_dict = filter_by_storey(adjacent_spaces_dict, space_storey_dict)
    # print(space_adj_dict)
    # output_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\output'
    # output_json_path = os.path.join(output_path, f"{model_name}_adjacent_spaces.json")
    #
    # # Write the dictionary to a JSON file
    # with open(output_json_path, 'w') as json_file:
    #     json.dump(space_adj_dict, json_file, indent=4)
    #
    # print(f"Adjacent spaces dictionary has been written to {output_json_path}")

