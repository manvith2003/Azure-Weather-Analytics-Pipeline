

bronze_path = "abfss://weather-data@<storage-account>.dfs.core.windows.net/bronze"

df_bronze = spark.read.json(bronze_path)

df_bronze.show(truncate=False)
