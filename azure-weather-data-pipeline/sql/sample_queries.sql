-- Sample Analytical Queries for Azure SQL Database

-- 1. View the top 10 hottest cities
SELECT TOP 10 
    city, 
    country, 
    max_temperature_c
FROM weather_gold
ORDER BY max_temperature_c DESC;

-- 2. View the top 10 most humid cities
SELECT TOP 10 
    city, 
    country, 
    avg_humidity
FROM weather_gold
ORDER BY avg_humidity DESC;

-- 3. Find cities with extreme wind speeds (above 50 kph)
SELECT 
    city, 
    country, 
    max_wind_kph, 
    latest_weather_time
FROM weather_gold
WHERE max_wind_kph > 50.0
ORDER BY max_wind_kph DESC;

-- 4. Calculate total average metrics across all tracked cities
SELECT 
    COUNT(DISTINCT city) AS total_cities_tracked,
    ROUND(AVG(max_temperature_c), 2) AS global_avg_max_temp,
    ROUND(AVG(CAST(avg_humidity AS FLOAT)), 2) AS global_avg_humidity
FROM weather_gold;
