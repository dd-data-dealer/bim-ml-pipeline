from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from sympy.solvers.ode.single import solver_map

from .parser import open_ifc, extract_products
from .schemas import RAW_PRODUCT_SCHEMA
from .transformer import create_silver_products
import ifcopenshell.util.element
# gold
from .transformation.wall_features import wall_features_partition
from .schemas import WALL_FEATURE_SCHEMA


from collections import Counter



FILE_PATH = "data/raw/IFC Schependomlaan.ifc"

model = open_ifc(FILE_PATH)

products = extract_products(model)
# print(len(products))
# for product in products[5:]:
#     print(product)

# checks
# types = Counter(product["element_type"] for product in products)
#
# for element_type, count in types.most_common():
#     print(element_type, count)

spark = (
    SparkSession.builder
    .appName("AIDataEngineering-MLProductionPipeline")
    .master("local[1]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    # .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    .getOrCreate()
)

products_df=spark.createDataFrame(products, schema=RAW_PRODUCT_SCHEMA)


products_df.write \
    .mode("overwrite") \
    .parquet("data/bronze/products")

# check content:

products_df.select(
    "element_type",
    "id",
    "properties"
).show(10, truncate=True)

# check if any with desctription:
# products_df.filter(
#     F.col("description").isNotNull()
# ).select(
#     "element_type",
#     "name",
#     "description"
# ).show(20, truncate=False)

# KZ 04.10.2026 checks before creating silver. validate bronze layer:
# 1 data profiling
#
# products_df.printSchema()
#
# products_df.select("element_type").distinct().show(50, truncate=False)

# 2 null counts
# products_df.select([
#     F.sum(F.col(c).isNull().cast("int")).alias(c)
#     for c in products_df.columns
# ]).show()

# 3 duplicates on the IFC identifier:

# products_df.groupBy("global_id") \
#     .count() \
#     .filter(F.col("count") > 1) \
#     .show()
# print("check!!!")
# products_df.printSchema()

# ___________
# silver


silver_df = create_silver_products(products_df)

silver_df.show(10, truncate=False)
silver_df.printSchema()

silver_df.write \
    .mode("overwrite") \
    .parquet("data/silver/products")

print(products_df.is_cached)
print(silver_df.is_cached)


# -----------
# gold

# wall = model.by_type("IfcWall")[0]
#
# properties = ifcopenshell.util.element.get_psets(wall)

# print(properties)

# ------
# check
# for element_type in [
#     "IfcWall",
#     "IfcDoor",
#     "IfcWindow",
#     "IfcSlab",
#     "IfcBeam",
#     "IfcColumn",
# ]:
#     elements = model.by_type(element_type)
#
#     if elements:
#         psets = ifcopenshell.util.element.get_psets(elements[0])
#
#         print(f"\n--- {element_type} ---")
#         print(psets.get("BaseQuantities"))

# KZ 6 Oct 2026: after above check we decided not force all element types into one identical feature schema.
# Silver elements
#       ↓
# element_type
#       ├── Wall    → wall features    → model
#       ├── Window  → window features  → model
#       ├── Slab    → slab features    → model
#       └── Beam    → beam features    → model



walls_df = silver_df.filter(
    F.col("element_type") == "IfcWall"
)

wall_features_df = walls_df.mapInPandas(
    wall_features_partition,
    schema=WALL_FEATURE_SCHEMA
)

# wall_features_df.show(truncate=False)

spark.stop()
print(products_df.is_cached)
print(silver_df.is_cached)