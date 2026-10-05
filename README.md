
## Current Pipeline

The pipeline currently ingests BIM data from IFC files and converts raw IFC products into structured Spark data.

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
Normalize selected product attributes
   |
   v
RAW_PRODUCT_SCHEMA
   |
   v
PySpark DataFrame
   |
   v
Bronze layer (Parquet)  3,822 raw products (5 oct 2026)
   |
   v
filter + clean
   |
   v
SILVER              physical BIM elements
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

Data cleaning, filtering, enrichment, and feature preparation will be performed in the **Silver** and **Gold** layers rather than during Bronze ingestion.