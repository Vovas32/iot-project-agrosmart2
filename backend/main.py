from fastapi import FastAPI
from azure.storage.blob import BlobServiceClient
import json
from datetime import datetime

app = FastAPI()

# Here connection string should be inserted vvv 
AZURE_CONNECTION_STRING =                  "..."
CONTAINER_NAME = "iot-data"

blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service.get_container_client(CONTAINER_NAME)

# Creating a container, if it doesn't exist :/  vvv
try:
    container_client.create_container()
except:
    pass

# Saving irrigation state vvv
irrigation_state = {
    "irrigationOn": False
}


@app.post("/api/device/data")
def receive_data(data: dict):
    global irrigation_state

    # AutoIrrigation Logic vvv
    if data.get("soilMoisture", 100) < 40:
        irrigation_state["irrigationOn"] = True
    else:
        irrigation_state["irrigationOn"] = False

    blob_name = f"{datetime.utcnow().isoformat()}.json"
    container_client.upload_blob(
        blob_name,
        json.dumps(data),
        overwrite=True
    )

    return {
        "status": "ok",
        "irrigationOn": irrigation_state["irrigationOn"]
    }


@app.get("/api/device/data")
def get_data():
    blobs = container_client.list_blobs()
    result = []
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        content = blob_client.download_blob().readall()
        result.append(json.loads(content))
    return result

@app.get("/api/device/average")
def average_temperature():
    blobs = container_client.list_blobs()
    temps = []
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        content = blob_client.download_blob().readall()
        data = json.loads(content)
        temps.append(data["temperature"])
    if temps:
        return {"average_temperature": sum(temps)/len(temps)}
    return {"average_temperature": None}

@app.get("/api/device/alerts")
def low_soil_moisture_alert(threshold: int = 35):
    blobs = container_client.list_blobs()
    alerts = []
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        data = json.loads(blob_client.download_blob().readall())
        if data["soilMoisture"] < threshold:
            alerts.append(data)
    return {"alerts": alerts}

@app.get("/api/device/command")
def get_device_command():
    return irrigation_state