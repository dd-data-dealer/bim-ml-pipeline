
## Current Pipeline

The pipeline ingests BIM data from IFC files and transforms raw IFC products into structured Spark datasets using a Bronze → Silver → Gold architecture.

```text
IFC file
   |
   v
IfcOpenShell
   |
   v
Extract IfcProduct objects
   |
   v
Extract + flatten IFC property/quantity sets
   |
   v
Normalize selected product attributes
   |
   v
RAW_PRODUCT_SCHEMA
   |
   v
PySpark DataFrame
   |
   v
BRONZE (Parquet)
3,822 raw products (5 Oct 2026)
Metadata + IFC properties preserved
   |
   v
Filter + clean
   |
   v
SILVER (Parquet)
Physical BIM elements + IFC properties
   |
   v
Filter by element type
   |
   v
Extract element-specific features
   |
   v
Convert numerical properties to float
   |
   v
GOLD (Parquet)
Structured ML features
```

### Raw IFC Extraction

IFC files are parsed using `IfcOpenShell`. Each `IfcProduct` is extracted into a normalized record containing:

- `id`
- `global_id`
- `element_type`
- `name`
- `description`
- `object_type`
- `tag`
- `properties`

The `properties` field contains extracted IFC property and quantity values, flattened into a dictionary.

The structure of extracted records is enforced using `RAW_PRODUCT_SCHEMA`.

### Bronze Layer

The Bronze layer stores the structured representation of the source IFC data with minimal transformation.

```text
data/bronze/products/
```

Products are stored as **Parquet** files using PySpark.

The Bronze layer preserves source data as closely as possible, including missing values.

For example, the current Schependomlaan IFC model does not populate the `Description` attribute for its products. Therefore, `description` remains `NULL` in Bronze rather than being filled or removed.

**Current dataset:**

- Source: Schependomlaan IFC model
- Extracted `IfcProduct` objects: **3,822**
- Storage format: **Parquet**
- IFC properties and quantities preserved

### Silver Layer

The Silver layer filters and cleans Bronze data while retaining IFC properties required for feature engineering.

```text
data/silver/products/
```

**Transformations:**

- Exclude nonphysical IFC entities such as `IfcSite`, `IfcBuilding`, `IfcBuildingStorey`, and `IfcSpace`.
- Remove unused metadata columns: `description` and `object_type`.
- Preserve identifiers, element types, names, tags, and IFC properties.
- Store the resulting dataset in Parquet format.

**Silver schema:**

```text
id
global_id
element_type
name
tag
properties
```

The `properties` column uses Spark's `MapType(StringType(), StringType())`.

Consequently, numerical IFC property values are represented as strings and require conversion before being used as numerical ML features.

### Gold Layer

The Gold layer transforms cleaned BIM elements into structured, element-specific features suitable for machine learning.

The first implemented feature extractor processes **IfcWall** elements.

**Processing steps:**

1. Filter Silver records where `element_type == "IfcWall"`.
2. Process wall records using `mapInPandas()`.
3. Extract geometrical properties using `extract_wall_features()`.
4. Convert numerical property values from strings to Python floats.
5. Validate the resulting structure against `WALL_FEATURE_SCHEMA`.
6. Save Gold features as Parquet files.

**Current wall features:**

| Feature | Type |
|---|---|
| `element_id` | Integer |
| `element_type` | String |
| `length` | Double |
| `height` | Double |
| `width` | Double |
| `gross_footprint_area` | Double |
| `net_footprint_area` | Double |
| `gross_side_area` | Double |
| `net_side_area` | Double |
| `gross_volume` | Double |
| `net_volume` | Double |

Missing numerical properties are represented as `NULL`.

**Validation:**

Gold wall feature extraction now produces populated numerical values instead of the previously observed `NULL` values.

### Known Issues and Next Steps

**Spark task-size warning**

Spark reports serialized tasks exceeding the recommended 1,000 KiB threshold.

This warning is separate from the size of the input DataFrame and may be related to how Python collections are transferred into Spark.

The issue remains under investigation.

**Next steps:**

- Investigate oversized serialized Spark tasks.
- Validate Gold feature completeness, data types, and IFC measurement units.
- Extend feature extraction to additional BIM element types, including `IfcWindow`, `IfcSlab`, and `IfcBeam`.
- Prepare Gold datasets for ML model training and evaluation.
