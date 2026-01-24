# Silver Transformation
# Cleans and flattens raw JSON data

from pyspark.sql.functions import col, current_timestamp

bronze_path = "abfss://weather-data@<storage-account>.dfs.core.windows.net/bronze"
silver_path = "abfss://weather-data@<storage-account>.dfs.core.windows.net/silver"

df_bronze = spark.read.json(bronze_path)

df_silver = df_bronze.select(
    col("location.name").alias("city"),
    col("location.country").alias("country"),
    col("current.temp_c").alias("temperature_c"),
    col("current.humidity").alias("humidity"),
    col("current.wind_kph").alias("wind_kph"),
    col("current.last_updated").alias("weather_time"),
    current_timestamp().alias("ingestion_time")
)

df_silver.write.mode("overwrite").parquet(silver_path)
