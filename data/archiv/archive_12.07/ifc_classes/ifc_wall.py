import ifcopenshell.geom
import numpy as np

class IfcWall:
    def __init__(self, wall):
        self.wall = wall
        self.polyline = self.extract_polyline()
        self.openings = self.extract_openings()  # New: Method to extract openings

    @property
    def id(self):
        return self.wall.id()

    @property
    def name(self):
        return self.wall.Name

    @property
    def polyline_points(self):
        if self.polyline:
            return [p.Coordinates for p in self.polyline.Points]
        return None

    @property
    def start_point(self):
        if self.polyline:
            return np.array(self.polyline.Points[0].Coordinates)
        return None

    @property
    def end_point(self):
        if self.polyline:
            return np.array(self.polyline.Points[-1].Coordinates)
        return None

    def extract_polyline(self):
        if self.wall.Representation:
            for representation in self.wall.Representation.Representations:
                if representation.RepresentationType == "Curve2D":
                    for item in representation.Items:
                        if item.is_a('IfcPolyline'):
                            return item
        return None

    def extract_openings(self):
        openings = []
        if self.wall.HasOpenings:
            for opening_rel in self.wall.HasOpenings:
                opening_element = opening_rel.RelatedOpeningElement
                if opening_element and opening_element.Representation:
                    context = opening_element.Representation.Representations[0].ContextOfItems
                    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), opening_element)
                    vertices = self.extract_vertices(shape)
                    openings.append({
                        'element': opening_element,
                        'vertices': vertices
                    })
        return openings if openings else None  # Return None if no openings found

    def extract_vertices(self, shape):
        vertices = shape.geometry.verts
        grouped_vertices = []
        for i in range(0, len(vertices), 3):
            grouped_vertices.append(vertices[i:i+3])
        return np.array(grouped_vertices)
