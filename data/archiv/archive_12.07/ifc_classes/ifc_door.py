class IfcDoor:
    def __init__(self, door):
        self.door = door
        self._placement = None
        self._shape = None  # Private variable to store the value

    @property
    def id(self):
        return self.door.id()

    @property
    def name(self):
        return self.door.Name

    @property
    def placement(self):
        return self._placement

    @placement.setter
    def placement(self, value):
        self._placement = value

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        self._shape = value

    @property
    def vertices(self):
        if self.shape:
            settings = ifcopenshell.geom.settings()
            shape = ifcopenshell.geom.create_shape(settings, self.door)
            return self.extract_vertices(shape)
        return None

    @property
    def middle_point(self):
        if self.vertices:
            min_point = np.min(self.vertices, axis=0)
            max_point = np.max(self.vertices, axis=0)
            middle_point = (min_point + max_point) / 2.0
            return middle_point
        return None

    def extract_vertices(self, shape):
        vertices = shape.geometry.verts
        grouped_vertices = []
        for i in range(0, len(vertices), 3):
            grouped_vertices.append(vertices[i:i + 3])
        return np.array(grouped_vertices)
