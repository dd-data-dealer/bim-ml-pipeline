from pyspark.sql import SparkSession
import pyspark.sql.functions as F

from .parser import open_ifc, extract_products
from .schemas import RAW_PRODUCT_SCHEMA
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

# products_df.select(
#     "element_type",
#     "name",
#     "description",
#     "object_type"
# ).show(10, truncate=True)

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
products_df.printSchema()

products_df.select("element_type").distinct().show(50, truncate=False)

# 2 null counts
products_df.select([
    F.sum(F.col(c).isNull().cast("int")).alias(c)
    for c in products_df.columns
]).show()

# 3 duplicates on the IFC identifier:

products_df.groupBy("global_id") \
    .count() \
    .filter(F.col("count") > 1) \
    .show()

spark.stop()
