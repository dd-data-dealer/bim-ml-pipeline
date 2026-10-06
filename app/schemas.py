from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)


RAW_PRODUCT_SCHEMA = StructType([
    StructField("id", IntegerType(), False),
    StructField("global_id", StringType(), True),
    StructField("element_type", StringType(), False),
    StructField("name", StringType(), True),
    StructField("description", StringType(), True),
    StructField("object_type", StringType(), True),
    StructField("tag", StringType(), True),
])


WALL_FEATURE_SCHEMA = StructType([
    StructField("element_id", IntegerType(), True),
    StructField("element_type", StringType(), False),
    StructField("length", DoubleType(), True),
    StructField("height", DoubleType(), True),
    StructField("width", DoubleType(), True),
    StructField("gross_footprint_area", DoubleType(), True),
    StructField("net_footprint_area", DoubleType(), True),
    StructField("gross_side_area", DoubleType(), True),
    StructField("net_side_area", DoubleType(), True),
    StructField("gross_volume", DoubleType(), True),
    StructField("net_volume", DoubleType(), True),
])