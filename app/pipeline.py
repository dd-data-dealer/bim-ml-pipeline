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

# test
import pickle



from collections import Counter

FILE_PATH = "data/raw/IFC Schependomlaan.ifc"

model = open_ifc(FILE_PATH)

products = extract_products(model)
# KZ 9th oct
# print(
#     "Products size (MB):",
#     round(len(pickle.dumps(products)) / 1024**2, 2)
# )
# 1.2 new


spark = (
    SparkSession.builder
    .appName("AIDataEngineering-MLProductionPipeline")
    .master("local[1]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    # .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    .getOrCreate()
)

# # 1.1 old
products_df=spark.createDataFrame(products, schema=RAW_PRODUCT_SCHEMA)

# 1.1. new
# products_rdd = spark.sparkContext.parallelize(
#     products,
#     numSlices=17
# )

# 1.1. new
# products_df = spark.createDataFrame(
#     products_rdd,
#     schema=RAW_PRODUCT_SCHEMA
# )
# kz 9th oct test:
print("Partitions:", products_df.rdd.getNumPartitions())

# ___________
# bronze

products_df.write \
    .mode("overwrite") \
    .parquet("data/bronze/products")

# ___________
# silver


silver_df = create_silver_products(products_df)
# print("check after silver df creation")

print("Silver partitions:", silver_df.rdd.getNumPartitions())
# silver_df.show(10, truncate=False)
# silver_df.printSchema()

silver_df.write \
    .mode("overwrite") \
    .parquet("data/silver/products")


# -----------
# gold



walls_df = silver_df.filter(
    F.col("element_type") == "IfcWall"
)

wall_features_df = walls_df.mapInPandas(
    wall_features_partition,
    schema=WALL_FEATURE_SCHEMA
)

wall_features_df.show(3, truncate=False)

# print(spark.sparkContext.getConf().get("spark.driver.memory", "Not explicitly set"))
# jvm = spark.sparkContext._jvm
# # max partitoin size
# print(f"Max partition size: {int(spark.conf.get('spark.sql.files.maxPartitionBytes').removesuffix('b')) / 1024**2:.2f} MB")
# # max driver
# print(f"Max JVM heap: {jvm.java.lang.Runtime.getRuntime().maxMemory() / 1024**2:.2f} MB")

spark.stop()

