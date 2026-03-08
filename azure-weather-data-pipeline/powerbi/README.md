# Power BI Dashboard Setup

This guide explains how to connect Power BI to the Azure SQL Database to visualize the aggregated weather data (Gold layer).

## 1. Connect to Azure SQL Database
1. Open Power BI Desktop.
2. Click on **Get Data** -> **Azure** -> **Azure SQL Database** -> **Connect**.
3. In the popup window:
   - **Server**: Enter your Azure SQL server name (e.g., `myserver.database.windows.net`).
   - **Database**: Enter the database name.
   - **Data Connectivity mode**: Choose **DirectQuery** (recommended for near real-time updates) or **Import**.
4. Click **OK**.
5. When prompted for credentials, select **Database** and enter the username and password created for the Azure SQL Database.
6. Select the `weather_gold` table. Click **Load**.

## 2. Recommended Visualizations

### A. Global Temperature Map
- **Visual Type**: Map
- **Location**: `city` or `country`
- **Bubble Size** or **Tooltips**: `max_temperature_c`

### B. Humidity Comparison
- **Visual Type**: Clustered Column Chart
- **X-axis**: `city`
- **Y-axis**: `avg_humidity`

### C. Extreme Wind Speeds
- **Visual Type**: Table or Matrix
- **Data fields**: `city`, `country`, `max_wind_kph`, `latest_weather_time`
- **Filter**: Filter by `max_wind_kph` > a specific threshold.

### D. High-Level Metrics (Cards)
- **Visual Type**: Card
- Create cards for:
  - Total Cities Tracked (`Count (Distinct) of city`)
  - Overall Max Temperature (`Max of max_temperature_c`)
  - Last Updated Time (`Max of latest_weather_time`)

## 3. Publishing
Once the dashboard is designed, click **Publish** in the Home tab to publish the report to your Power BI Workspace online. You can then set up scheduled refreshes if using Import mode, or rely on DirectQuery for live data.

This dashboard connects to Azure SQL Database and visualizes the Gold layer.

## Visuals
- City-wise temperature
- Humidity by city
- Wind speed
- Latest weather update timestamp

## Data Source
Azure SQL Database → weather_gold table

