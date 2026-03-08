# Azure Weather Data Engineering Pipeline

This project demonstrates an end-to-end Azure Data Engineering pipeline that ingests real-time weather data from a REST API, processes it using Medallion Architecture (Bronze, Silver, Gold), and serves analytics-ready data through Azure SQL Database and Power BI.

---

## Project Overview

The pipeline is designed to simulate a real-world data engineering workflow on Azure. It covers data ingestion, storage, transformation, aggregation, and visualization using industry-standard tools and practices.

---

## Architecture

![Azure Data Pipeline Architecture](architecture/azure_weather_architecture_diagram.png)

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

- **Azure Data Factory** – Data ingestion and orchestration  
- **Azure Data Lake Storage Gen2** – Centralized data storage  
- **Azure Databricks** – Distributed data processing using PySpark  
- **Azure SQL Database** – Analytics-ready relational storage  
- **Power BI** – Data visualization and reporting  
- **Python, PySpark, SQL, Bash**  

---

## Repository Structure

```text
azure-weather-data-pipeline/
├── adf/
│   ├── linkedServices.json        # ADF connection settings (ADLS, SQL, Databricks, API)
│   └── pipeline.json              # ADF pipeline definition (Data movement & Orchestration)
├── architecture/
│   └── architecture.txt           # Text-based architecture diagram
├── databricks/
│   ├── bronze_ingestion.py        # Validates and loads raw API JSON
│   ├── silver_transform.py        # Cleans, flattens, and type-casts data to Parquet
│   ├── gold_aggregation.py        # Aggregates city-level weather metrics to Parquet
│   └── mount_storage.py           # Mounts ADLS to Databricks DBFS securely
├── infrastructure/
│   └── setup_azure_resources.sh   # Bash script to provision ADLS Gen2 using Azure CLI
├── powerbi/
│   └── README.md                  # Instructions for Power BI connection and visuals
├── sample_data/
│   └── weather_sample.json        # Example raw API response
└── sql/
    ├── create_weather_gold_table.sql # SQL DDL for Gold layer serving table
    └── sample_queries.sql         # Example analytical queries
```

---

## Getting Started

1. **Deploy Infrastructure**:
   - Install Azure CLI and `az login`.
   - Run `infrastructure/setup_azure_resources.sh` to create the Resource Group and Data Lake Storage with `bronze`, `silver`, and `gold` containers.

2. **Configure Databricks**:
   - Create an Azure Databricks workspace.
   - Run `databricks/mount_storage.py` (after configuring your Service Principal secrets) to mount the ADLS containers.
   - Import the python files in `databricks/` as notebooks.

3. **Set Up Azure SQL**:
   - Provision an Azure SQL Database.
   - Run the script in `sql/create_weather_gold_table.sql` to create the target table.

4. **Deploy Data Factory**:
   - Create an Azure Data Factory instance.
   - Use the JSON files in `adf/` to create linked services and the main orchestration pipeline. Set your specific connection string secrets.

5. **Visualization**:
   - Refer to `powerbi/README.md` to connect your dashboard to Azure SQL.
