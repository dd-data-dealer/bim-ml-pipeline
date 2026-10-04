from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
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