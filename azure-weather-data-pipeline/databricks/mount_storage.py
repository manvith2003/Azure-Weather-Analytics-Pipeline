# Mount Azure Data Lake Storage Gen2 to Databricks using Service Principal
# This script sets up the mount points for Bronze, Silver, and Gold containers.

def mount_adls(storage_account_name, container_name, client_id, tenant_id, client_secret):
    mount_point = f"/mnt/{storage_account_name}/{container_name}"
    source = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/"

    # Check if the mount point already exists
    if any(mount.mountPoint == mount_point for mount in dbutils.fs.mounts()):
        print(f"Mount point {mount_point} already exists. Unmounting...")
        dbutils.fs.unmount(mount_point)

    configs = {
        "fs.azure.account.auth.type": "OAuth",
        "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
        "fs.azure.account.oauth2.client.id": client_id,
        "fs.azure.account.oauth2.client.secret": client_secret,
        "fs.azure.account.oauth2.client.endpoint": f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
    }

    try:
        dbutils.fs.mount(
            source=source,
            mount_point=mount_point,
            extra_configs=configs
        )
        print(f"Successfully mounted {container_name} container to {mount_point}")
    except Exception as e:
        print(f"Failed to mount {container_name}: {str(e)}")


storage_account = "<YOUR_STORAGE_ACCOUNT_NAME>"
client_id = dbutils.secrets.get(scope="azure-kv", key="sp-client-id")
tenant_id = dbutils.secrets.get(scope="azure-kv", key="sp-tenant-id")
client_secret = dbutils.secrets.get(scope="azure-kv", key="sp-client-secret")

containers = ["bronze", "silver", "gold"]

for container in containers:
    mount_adls(storage_account, container, client_id, tenant_id, client_secret)

# Verify mounts
display(dbutils.fs.mounts())
