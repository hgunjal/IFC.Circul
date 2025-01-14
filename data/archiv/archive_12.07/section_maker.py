from ifc_classes.ifc_project import IfcProject


file_path = r'C:\Users\harsh\Documents\Master Thesis\ifc_processing\AC20-FZK-Haus.ifc'

def main():
    model = IfcProject(file_path)
    print(model.schema)
    print(model.by_id(21))


if __name__ == "__main__":
    main()