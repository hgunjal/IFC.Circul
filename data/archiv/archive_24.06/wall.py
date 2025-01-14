# -*- coding: cp1252 -*-
import ifcopenshell
import ifcopenshell.util.selector
file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'
ff = ifcopenshell.open(file_path)
wall = ff.by_type("IfcWallstandardcase")

for w in wall:
    print (w.Name)
# #267=IfcWallStandardCase('3L0b4BAlb9wRqiy6SvBDii',#41,'Basic Wall:Generic - 200mm:381109',$,'Basic Wall:Generic - 200mm:1044',#219,#265,'381109')

# print(wall.Representation)
# #265=IfcProductDefinitionShape($,$,(#224,#263))

# print(wall.ObjectPlacement)
# #219=IfcLocalPlacement(#129,#218)

# print(wall.HasOpenings)
# #295=IfcRelVoidsElement('1CuejoVD9FueFp2MOmBFLk',#41,$,$,#267,#290),)

# print("wall.ConnectedTo",wall.ConnectedTo)
# #2510=IfcRelConnectsPathElements('1LmmAoCRPD6wTg67$ubp1I',#41,'3L0b4BAlb9wRqiy6SvBDii|3L0b4BAlb9wRqiy6SvBDjO','Structural',$,#267,#580,,(),(),.ATEND.,.ATSTART.), #2515=IfcRelConnectsPathElements('0Fz8qmuLD7pwxKf3gsgxyk',#41,'3L0b4BAlb9wRqiy6SvBDii|3L0b4BAlb9wRqiy6SvBDjQ','Structural',$,#267,#630,(),(),.ATSTART.,.ATSTART.) #2519=IfcRelConnectsPathElements('22B1kEbQfA_896Mh6mCoCT',#41,'3L0b4BAlb9wRqiy6SvBDii|3L0b4BAlb9wRqiy6SvBDjU','Structural',$,#267,#680,(),(),.ATSTART.,.ATEND.))

# print(wall.ContainedInStructure)
# #2310=IfcRelContainedInSpatialStructure('1w2kgyXAD2C9c7QsP4npsv',#41, $,$,(#173,#267,#366,#426,#476,#530,#580,#630,#680,#730,#830,#884,#984,#1034,#1134,#1184,#1260,#1310,#1360,#1410),#130),)

# print(wall.Decomposes)
# ()

# print(wall.FillsVoids)
# # PJAEE, 17 (9) (2020) 8835 ()

# print(wall.HasAssociations)
# #2393=IfcRelAssociatesMaterial('20vhLKyur9m81aPlR20782',#41,$,$,(#267), #312),)

# print(wall.IsExternal)

# # print(wall.HasStructuralMember)