def extract_wall_features(element: dict) -> dict:
    properties = element.get("properties") or {}

    return {
        "element_id": element.get("id"),
        "element_type": "Wall",
        "length": properties.get("Length"),
        "height": properties.get("Height"),
        "width": properties.get("Width"),
        "gross_footprint_area": properties.get("GrossFootprintArea"),
        "net_footprint_area": properties.get("NetFootprintArea"),
        "gross_side_area": properties.get("GrossSideArea"),
        "net_side_area": properties.get("NetSideArea"),
        "gross_volume": properties.get("GrossVolume"),
        "net_volume": properties.get("NetVolume"),
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


        yield pd.DataFrame(results)