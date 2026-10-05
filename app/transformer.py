from pyspark.sql import DataFrame
from pyspark.sql.functions import col

# we exclude them as
EXCLUDED_ELEMENT_TYPES = [
    "IfcSite",
    "IfcBuilding",
    "IfcBuildingStorey",
    "IfcSpace",
]

# !!!!! tylda to filetr el_type this is not included in excluded list.
def create_silver_products(df: DataFrame) -> DataFrame:
    return (
        df
        .filter(~col("element_type").isin(EXCLUDED_ELEMENT_TYPES))
        .drop("description", "object_type")
    )