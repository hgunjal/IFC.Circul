import ifcopenshell.geom
import ifcopenshell.util.shape
from .ifc_element import IfcElement
import numpy as np

class IfcDoor(IfcElement):
    def __init__(self, element):
        super().__init__(element)
