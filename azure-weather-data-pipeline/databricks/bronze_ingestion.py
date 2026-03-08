# Bronze Ingestion
# Reads raw JSON weather data from the Bronze container in ADLS.

from pyspark.sql.functions import current_timestamp, input_file_name

# Assuming storage is mounted via mount_storage.py
bronze_mount_path = "/mnt/<YOUR_STORAGE_ACCOUNT_NAME>/bronze"
raw_data_path = f"{bronze_mount_path}/*.json"

# Read raw JSON data
# Note: Weather API responses might be multi-line JSON or Single-line
# Using multiLine=True to be safe for complex nested JSONs
print(f"Reading raw data from: {raw_data_path}")

try:
    df_bronze = spark.read.option("multiLine", True).json(raw_data_path)
    
    # Optional: Add metadata for traceability
    df_bronze_with_meta = df_bronze.withColumn("ingestion_timestamp", current_timestamp()) \
                                   .withColumn("source_file", input_file_name())
    
    print("Bronze data loaded successfully.")
    display(df_bronze_with_meta.limit(10))

except Exception as e:
    print(f"Error reading bronze data: {str(e)}")
