# Gold Aggregation
# Creates business-ready aggregated dataset

from pyspark.sql.functions import max

silver_path = "abfss://weather-data@<storage-account>.dfs.core.windows.net/silver"
gold_path = "abfss://weather-data@<storage-account>.dfs.core.windows.net/gold"

df_silver = spark.read.parquet(silver_path)

df_gold = (
    df_silver
    .groupBy("city", "country")
    .agg(
        max("weather_time").alias("latest_weather_time"),
        max("temperature_c").alias("temperature_c"),
        max("humidity").alias("humidity"),
        max("wind_kph").alias("wind_kph")
    )
)

df_gold.write.mode("overwrite").parquet(gold_path)
