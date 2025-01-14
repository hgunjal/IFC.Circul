# -*- coding: cp1252 -*-
import ifcopenshell

file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
ff = ifcopenshell.open(file_path)

# Retrieve all IfcWall instances
walls = ff.by_type("IfcWall")

# Initialize lists to store external and internal walls
external_walls = []
internal_walls = []

# Iterate through all walls
for wall in walls:
    # Check if the wall has a property set indicating it's external
    is_external = False
    print(f"Wall: {wall.GlobalId}, Name: {wall.Name}")
    for pset in wall.IsDefinedBy:
        print(f"  Property Set: {pset}")
        if pset.is_a("IfcRelDefinesByProperties"):
            print(f"    Property Definition: {pset.RelatingPropertyDefinition}")
            if pset.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                for prop in pset.RelatingPropertyDefinition.HasProperties:
                    print(f"      Property: {prop.Name}, Value: {prop.NominalValue}")
                    if prop.is_a("IfcPropertySingleValue") and prop.Name == "IsExternal" and prop.NominalValue.wrappedValue:
                        is_external = True
                        break
        

