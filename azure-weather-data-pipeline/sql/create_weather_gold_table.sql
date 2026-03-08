-- Azure SQL Database - Gold Layer Schema
-- This table matches the schema of the aggregated dataset produced by databricks/gold_aggregation.py

IF OBJECT_ID('weather_gold', 'U') IS NOT NULL
    DROP TABLE weather_gold;

CREATE TABLE weather_gold (
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latest_weather_time DATETIME2,
    max_temperature_c FLOAT,
    avg_humidity INT,
    max_wind_kph FLOAT,
    PRIMARY KEY (city, country)
);
