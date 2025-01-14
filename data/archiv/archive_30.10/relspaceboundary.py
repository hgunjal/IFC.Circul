import ifcopenshell

# Load the IFC file
file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\Circul.IFC\models\NBU_MedicalClinic_Arch.ifc'
model = ifcopenshell.open(file_path)

# Get the specific spaces by their GUIDs
s1 = model.by_guid('0ClPCUC7jCQRnj1dhupHsn')
s2 = model.by_guid('0ClPCUC7jCQRnj1dhupHcN')

# Print basic information about the spaces
print(f"Space 1 Info: {s1.get_info()}")
print(f"Space 2 Info: {s2.get_info()}")

# Retrieve all IfcRelSpaceBoundary objects related to both spaces
rel_space_boundaries = model.by_type('IfcRelSpaceBoundary')

# Initialize empty list to store matching boundaries
matching_boundaries = []

# Compare the virtual boundaries between s1 and s2
for rel1 in rel_space_boundaries:
    if rel1.RelatingSpace == s1 and rel1.RelatedBuildingElement is None:
        # Print boundary details for debugging
        print(f"\nVirtual Boundary in s1: {rel1.get_info()}")

        for rel2 in rel_space_boundaries:
            if rel2.RelatingSpace == s2 and rel2.RelatedBuildingElement is None:
                # Print boundary details for debugging
                print(f"\nVirtual Boundary in s2: {rel2.get_info()}")

                # Compare the connection geometries
                if rel1.ConnectionGeometry and rel2.ConnectionGeometry:
                    # Access the surface geometries for comparison
                    surface1 = rel1.ConnectionGeometry.SurfaceOnRelatingElement
                    surface2 = rel2.ConnectionGeometry.SurfaceOnRelatingElement

                    # Debugging output for surface comparison
                    print(f"\nComparing surface of s1: {surface1}")
                    print(f"With surface of s2: {surface2}")

                    # Compare surfaces (you may want to compare more specific properties)
                    if surface1 == surface2:
                        # We have a match of virtual boundary surfaces
                        matching_boundaries.append((rel1, rel2))
                        print(f"\nShared Virtual Boundary found between s1 and s2")
                        print(f"Boundary in s1: {rel1.get_info()}")
                        print(f"Boundary in s2: {rel2.get_info()}")

# If no shared boundary was found
if not matching_boundaries:
    print("\nNo shared virtual boundary found between s1 and s2.")
