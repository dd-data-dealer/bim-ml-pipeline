def to_float(value):
    if value is None or value == "":
        return None
    return float(value)


def extract_wall_features(element: dict) -> dict:
    properties = element.get("properties") or {}

    return {
        "element_id": element.get("id"),
        "element_type": "Wall",
        "length": to_float(properties.get("Length")),
        "height": to_float(properties.get("Height")),
        "width": to_float(properties.get("Width")),
        "gross_footprint_area": to_float(properties.get("GrossFootprintArea")),
        "net_footprint_area": to_float(properties.get("NetFootprintArea")),
        "gross_side_area": to_float(properties.get("GrossSideArea")),
        "net_side_area": to_float(properties.get("NetSideArea")),
        "gross_volume": to_float(properties.get("GrossVolume")),
        "net_volume": to_float(properties.get("NetVolume")),
    }


from typing import Iterator
import pandas as pd


def wall_features_partition(
    batches: Iterator[pd.DataFrame]
) -> Iterator[pd.DataFrame]:

    for batch in batches:
        results = []

        for _, row in batch.iterrows():
            element = row.to_dict()
            # 7/10 check
            # print("ELEMENT:")
            # print(element)

            features = extract_wall_features(element)
            results.append(features)
            if len(results) < 3:
                print("11/10 check")
                print(features)
                print(type(features["length"]))


        yield pd.DataFrame(results)