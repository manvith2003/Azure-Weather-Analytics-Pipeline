# Gold Aggregation
# Creates business-ready aggregated dataset

from pyspark.sql.functions import max, round, avg

silver_mount_path = "/mnt/<YOUR_STORAGE_ACCOUNT_NAME>/silver"
gold_mount_path = "/mnt/<YOUR_STORAGE_ACCOUNT_NAME>/gold"

print(f"Reading from Silver: {silver_mount_path}")
df_silver = spark.read.parquet(silver_mount_path)

# Aggregate data by city and country to get the latest weather info
# In this specific case, if we have historical data, we might want the absolute latest row
# But for typical aggregation, let's say we want max temp and average humidity per city
df_gold = (
    df_silver
    .groupBy("city", "country")
    .agg(
        max("weather_time").alias("latest_weather_time"),
        round(max("temperature_c"), 2).alias("max_temperature_c"),
        round(avg("humidity"), 0).cast("integer").alias("avg_humidity"),
        round(max("wind_kph"), 2).alias("max_wind_kph")
    )
)

print(f"Writing Aggregated Data to Gold (Parquet): {gold_mount_path}")
# We might want to save this as a Delta table or just Parquet
df_gold.write.mode("overwrite").parquet(gold_mount_path)

print("Gold aggregation completed.")
display(df_gold.limit(5))
