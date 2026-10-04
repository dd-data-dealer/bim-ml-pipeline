import ifcopenshell


def open_ifc(file_path):
    return ifcopenshell.open(file_path)

def extract_products(model):
    elements = model.by_type("IfcProduct")
    output = []

    for element in elements:
        info = element.get_info()

        product = {
            "id": info["id"],
            "global_id": info.get("GlobalId"),
            "element_type": info["type"],
            "name": info.get("Name"),
            "description": info.get("Description"),
            "object_type": info.get("ObjectType"),
            "tag": info.get("Tag"),
        }

        output.append(product)

    return output
