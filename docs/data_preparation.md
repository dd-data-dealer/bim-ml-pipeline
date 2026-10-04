## *1. Description of methods used before col selection*

## Data Profiling

Before defining the Silver layer, the Bronze dataset was profiled using PySpark to understand the available IFC product data and identify data-quality issues.

### Element Types

Distinct IFC product types were inspected:

```python
products_df.select("element_type").distinct().show(50, truncate=False)
```

The dataset contains physical building elements such as:

- `IfcWall`
- `IfcWallStandardCase`
- `IfcSlab`
- `IfcWindow`
- `IfcDoor`
- `IfcBeam`
- `IfcColumn`

It also contains spatial or structural IFC objects such as `IfcBuilding`, `IfcBuildingStorey`, `IfcSite`, and `IfcSpace`.

These categories will be evaluated separately when defining the ML-ready Silver dataset.

### Null Analysis

Null values were counted for every Bronze column:

```python
from pyspark.sql import functions as F

products_df.select([
    F.sum(F.col(c).isNull().cast("int")).alias(c)
    for c in products_df.columns
]).show()
```

Results for **3,822 products**:

| Column | Nulls |
|---|---:|
| `id` | 0 |
| `global_id` | 0 |
| `element_type` | 0 |
| `name` | 291 |
| `description` | 3,822 |
| `object_type` | 3,625 |
| `tag` | 404 |

Based on this profiling:

- `description` is not useful for the current dataset because it is 100% null.
- `object_type` has very low coverage and will not be included in the initial Silver dataset.
- `name` and `tag` remain potentially useful despite containing missing values.
- `global_id` and `element_type` have complete coverage.

### Global ID Uniqueness

IFC `GlobalId` is used as the primary cross-layer identifier for products. Duplicate values were checked with:

```python
products_df.groupBy("global_id") \
    .count() \
    .filter(F.col("count") > 1) \
    .show()
```

No duplicate `global_id` values were found.

### Next Step: IFC Property Extraction

The current Bronze dataset primarily contains product metadata. It does not yet contain sufficient numerical features for ML.

The next step is to inspect IFC property and quantity sets using:

```python
import ifcopenshell.util.element

wall = model.by_type("IfcWall")[0]

properties = ifcopenshell.util.element.get_psets(wall)

print(properties)
```

Available properties and quantities will be profiled before deciding which features should be extracted into the Silver and Gold layers.)