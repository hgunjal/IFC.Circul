import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import ifcopenshell.util.element
import ifcopenshell.util.placement
from ifcopenshell import geom

ifc_file = ifcopenshell.open(r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc')

for element in ifc_file.by_type('IfcWall'):
    settings = ifcopenshell.geom.settings()
    shape = ifcopenshell.geom.create_shape(settings, element)

    # Print shape metadata
    print(f"GUID: {shape.guid}")
    print(f"ID: {shape.id}")
    print(f"Element: {ifc_file.by_guid(shape.guid)}")
    print(f"Geometry ID: {shape.geometry.id}")

    # Extract the transformation matrix and location
    matrix = ifcopenshell.util.shape.get_shape_matrix(shape)
    location = matrix[:,3][0:3]
    print(f"Location: {location}")

    # Find the spatial container of an element
    container = ifcopenshell.util.element.get_container(element)
    print(f"The wall: {element.Name} is located on {container.Name}")






