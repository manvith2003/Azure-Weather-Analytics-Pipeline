#!/bin/bash
# Azure CLI script to provision the ADLS Gen2 storage account and containers

# This script assumes you are already logged in to Azure CLI
# If not, run standard 'az login' first.

# Set Variables
RESOURCE_GROUP="rg-weather-analytics-demo"
LOCATION="eastus"
# Ensure the storage account name is globally unique and all lowercase
STORAGE_ACCOUNT="dlweatheranalytics$RANDOM"
CONTAINERS=("bronze" "silver" "gold")

# Create Resource Group
echo "Creating Resource Group: $RESOURCE_GROUP in $LOCATION"
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Storage Account (To enable Data Lake Gen2, set --hierarchical-namespace to true)
echo "Creating Storage Account: $STORAGE_ACCOUNT"
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --kind StorageV2 \
    --enable-hierarchical-namespace true

# Get Storage Account Key
echo "Fetching Storage Account Key..."
ACCOUNT_KEY=$(az storage account keys list -g $RESOURCE_GROUP -n $STORAGE_ACCOUNT --query "[0].value" -o tsv)

# Create Containers
for container in "${CONTAINERS[@]}"
do
    echo "Creating Container: $container"
    az storage fs create -n $container --account-name $STORAGE_ACCOUNT --account-key $ACCOUNT_KEY
done

echo "================================================="
echo "Storage setup complete!"
echo "Resource Group: $RESOURCE_GROUP"
echo "Storage Account Name: $STORAGE_ACCOUNT"
echo "Containers Created: ${CONTAINERS[*]}"
echo "================================================="
