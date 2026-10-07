import ifcopenshell
import ifcopenshell.util.element



def open_ifc(file_path):
    return ifcopenshell.open(file_path)

# KZ 7/10 incorrect!!
# def extract_products(model):
#     elements = model.by_type("IfcProduct")
#     output = []
#
#     for element in elements:
#         info = element.get_info()
#
#         product = {
#             "id": info["id"],
#             "global_id": info.get("GlobalId"),
#             "element_type": info["type"],
#             "name": info.get("Name"),
#             "description": info.get("Description"),
#             "object_type": info.get("ObjectType"),
#             "tag": info.get("Tag"),
#         }
#
#         output.append(product)
#
#     return output


def extract_products(model):
    elements = model.by_type("IfcProduct")
    output = []

    for element in elements:
        info = element.get_info()

        properties = ifcopenshell.util.element.get_psets(element)

        # Flatten property sets / quantity sets into one dictionary
        flat_properties = {}

        for property_set in properties.values():
            for key, value in property_set.items():
                if key != "id":
                    flat_properties[key] = value

        product = {
            "id": info["id"],
            "global_id": info.get("GlobalId"),
            "element_type": info["type"],
            "name": info.get("Name"),
            "description": info.get("Description"),
            "object_type": info.get("ObjectType"),
            "tag": info.get("Tag"),
            "properties": flat_properties,
        }

        output.append(product)

    return output
