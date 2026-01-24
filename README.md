# Azure Weather Data Engineering Pipeline

This project demonstrates an end-to-end Azure Data Engineering pipeline that ingests real-time weather data from a REST API, processes it using Medallion Architecture (Bronze, Silver, Gold), and serves analytics-ready data through Azure SQL Database and Power BI.

---

## Project Overview

The pipeline is designed to simulate a real-world data engineering workflow on Azure. It covers data ingestion, storage, transformation, aggregation, and visualization using industry-standard tools and practices.

---

## Architecture

Weather API  
↓  
Azure Data Factory (REST API Ingestion)  
↓  
Azure Data Lake Storage Gen2  
- Bronze Layer: Raw JSON data  
- Silver Layer: Cleaned and structured Parquet data  
- Gold Layer: Aggregated, business-ready Parquet data  
↓  
Azure Databricks (PySpark Transformations)  
↓  
Azure SQL Database  
↓  
Power BI Dashboard  

---

## Technology Stack

- Azure Data Factory – Data ingestion and orchestration  
- Azure Data Lake Storage Gen2 – Centralized data storage  
- Azure Databricks – Distributed data processing using PySpark  
- Azure SQL Database – Analytics-ready relational storage  
- Power BI – Data visualization and reporting  
- Python, PySpark, SQL  

---

## Medallion Architecture

### Bronze Layer
- Stores raw weather data in JSON format
- No transformations applied
- Acts as the immutable source of truth

### Silver Layer
- Cleans and flattens nested JSON data
- Selects relevant columns
- Enforces schema and data types
- Stored in Parquet format

### Gold Layer
- Aggregates Silver data into business-ready datasets
- Contains latest weather metrics per city
- Optimized for reporting and analytics

---

## Data Pipeline Flow

1. Azure Data Factory ingests weather data from a REST API
2. Raw data is stored in ADLS Gen2 (Bronze layer)
3. Azure Databricks reads Bronze data and performs transformations
4. Cleaned data is written to Silver layer in Parquet format
5. Aggregated data is written to Gold layer
6. Gold data is loaded into Azure SQL Database
7. Power BI connects to Azure SQL Database for visualization

---

## Power BI Dashboard

The Power BI dashboard provides:
- City-wise temperature analysis
- Humidity and wind speed metrics
- Latest weather update timestamps

The dashboard connects directly to the Azure SQL Database Gold table.

---

## Repository Structure

