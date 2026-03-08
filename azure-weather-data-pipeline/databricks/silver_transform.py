# Silver Transformation
# Cleans and flattens raw JSON data from Bronze to Silver layer as Parquet.

from pyspark.sql.functions import col, current_timestamp, to_timestamp

# Assuming storage is mounted via mount_storage.py
bronze_mount_path = "/mnt/<YOUR_STORAGE_ACCOUNT_NAME>/bronze"
silver_mount_path = "/mnt/<YOUR_STORAGE_ACCOUNT_NAME>/silver"

# We read the latest data from bronze (or process incrementally depending on setup)
print(f"Reading from Bronze: {bronze_mount_path}")
df_bronze = spark.read.json(bronze_mount_path)

# Flatten nested JSON and cast data types
df_silver = df_bronze.select(
    col("location.name").alias("city").cast("string"),
    col("location.country").alias("country").cast("string"),
    col("current.temp_c").alias("temperature_c").cast("float"),
    col("current.humidity").alias("humidity").cast("integer"),
    col("current.wind_kph").alias("wind_kph").cast("float"),
    to_timestamp(col("current.last_updated"), "yyyy-MM-dd HH:mm").alias("weather_time"),
    current_timestamp().alias("silver_processing_time")
)

# Filter out bad records (e.g. missing city name)
df_silver_clean = df_silver.filter(col("city").isNotNull())

print(f"Writing Cleaned Data to Silver (Parquet): {silver_mount_path}")
# In a real scenario, you might partition by date or append
df_silver_clean.write.mode("overwrite").parquet(silver_mount_path)

print("Silver transformation completed.")
display(df_silver_clean.limit(5))
