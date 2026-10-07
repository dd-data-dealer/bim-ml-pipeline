### IFC Properties Extraction

Originally, `extract_products()` extracted only basic `IfcProduct` metadata:

```text
id
global_id
element_type
name
description
object_type
tag
```

IFC property and quantity sets were therefore lost before reaching the Silver layer. This caused Gold feature extraction to return `NULL` values for fields such as `Length`, `Height`, `Width`, `GrossVolume`, and `NetVolume`.

The parser was updated to extract IFC property and quantity sets using `IfcOpenShell`:

```python
properties = ifcopenshell.util.element.get_psets(element)
```

The property sets are flattened and stored in the `properties` field of each product.

Example:

```text
properties:
Length -> 1650.0
Height -> 345.0
Width -> 220.0
GrossVolume -> 0.125235
NetVolume -> 0.125235
```

The `properties` field is now included in `RAW_PRODUCT_SCHEMA` and preserved through the Bronze and Silver layers.

### Known Issue — Large Spark Task Size
KZ 7th Oct 2026

After adding IFC properties, significantly more data is passed from Python to Spark.

Spark reports:

```text
Stage contains a task of very large size (~11 MB).
The maximum recommended task size is 1000 KiB.
```

In some runs, the Python worker also reports:

```text
PythonRunner: Detected deadlock while completing task:
Attempting to kill Python Worker
```

The current implementation first creates all IFC products as a local Python list:

```python
products = extract_products(model)

products_df = spark.createDataFrame(
products,
schema=RAW_PRODUCT_SCHEMA
)
```

After adding IFC properties, this list contains both metadata and large property maps. Spark must serialize and distribute this collection, which can create oversized tasks and additional pressure on the Python worker.

#### Planned Fix

Split the collection into multiple Spark partitions before DataFrame creation:

```python
products_rdd = spark.sparkContext.parallelize(
products,
numSlices=8
)

products_df = spark.createDataFrame(
products_rdd,
schema=RAW_PRODUCT_SCHEMA
)
```

Verify the resulting partition count:

```python
print(products_df.rdd.getNumPartitions())
```

Longer term, consider avoiding materializing the complete IFC product dataset as one large Python list before passing it to Spark.