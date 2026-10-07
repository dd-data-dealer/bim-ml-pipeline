from app.transformation.wall_features import extract_wall_features


def test_extract_wall_features():
    element = {
        "properties": {
            "Length": 577.77,
            "Height": 510.0,
            "Width": 100.0,
            "GrossFootprintArea": 0.057,
            "NetFootprintArea": 0.057,
            "GrossSideArea": 0.329,
            "NetSideArea": 0.329,
            "GrossVolume": 0.0329,
            "NetVolume": 0.0329,
            "id": 13596,
        }
    }

    result = extract_wall_features(element)

    assert result["element_id"] == 13596
    assert result["element_type"] == "Wall"
    assert result["length"] == 577.77
    assert result["height"] == 510.0
    assert result["width"] == 100.0
    assert result["gross_volume"] == 0.0329


    # test for missing properties
def test_extract_wall_features_missing_properties():
    element = {"properties": None}

    result = extract_wall_features(element)

    assert result["element_id"] is None
    assert result["length"] is None
    assert result["height"] is None