import ifcopenshell
import ifcopenshell.util.element

import multiprocessing
import ifcopenshell.geom
file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
model = ifcopenshell.open(file_path)

print(model.schema) # May return IFC2X3, IFC4, or IFC4X3.

print(model.by_type("IfcDoor")) # Will return a list of mentioned entities

wall = model.by_type("IfcWall")[0]
# Walls are typically located on a storey, equipment might be located in spaces, etc
container = ifcopenshell.util.element.get_container(wall)
# The wall is located on Level 01
print(f"The wall is located on {container.Name}")


