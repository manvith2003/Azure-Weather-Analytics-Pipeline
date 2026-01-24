# Azure Data Factory Pipeline

## Pipeline Name
pl_weather_ingestion

## Description
This pipeline ingests real-time weather data from a REST API and stores raw JSON data in Azure Data Lake Storage Gen2 (Bronze layer).

## Components
- REST Linked Service
- REST Dataset (JSON)
- ADLS Gen2 Dataset
- Copy Data Activity

## Output
Raw weather data stored in ADLS Gen2 under the Bronze folder.
