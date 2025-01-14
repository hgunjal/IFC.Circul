class IfcElement:
    def __init__(self, ifc_element):
        self.ifc_element = ifc_element
        self.id = ifc_element.id()
