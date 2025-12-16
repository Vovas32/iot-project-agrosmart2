from fastapi import FastAPI
from azure.storage.blob import BlobServiceClient
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Connection string (should be secret!)
AZURE_CONNECTION_STRING = ""

CONTAINER_NAME = "iot-data"

blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service.get_container_client(CONTAINER_NAME)

# Create container if not exists
try:
    container_client.create_container()
except:
    pass

# Irrigation state
irrigation_state = {"irrigationOn": False}


@app.post("/api/device/data")
def receive_data(data: dict):
    global irrigation_state
    try:
        # Auto irrigation logic
        if data.get("soilMoisture", 100) < 40:
            irrigation_state["irrigationOn"] = True
        else:
            irrigation_state["irrigationOn"] = False

        blob_name = f"{datetime.utcnow().isoformat()}.json"
        container_client.upload_blob(blob_name, json.dumps(data), overwrite=True)

        return {"status": "ok", "irrigationOn": irrigation_state["irrigationOn"]}
    except Exception as e:
        logger.exception("Error in receive_data")
        return {"error": str(e)}


@app.get("/api/device/data")
def get_data():
    try:
        blobs = container_client.list_blobs()
        result = []
        for blob in blobs:
            blob_client = container_client.get_blob_client(blob)
            content = blob_client.download_blob().readall()
            result.append(json.loads(content))
        return result
    except Exception as e:
        logger.exception("Error in get_data")
        return {"error": str(e)}


@app.get("/api/device/average")
def average_temperature():
    try:
        blobs = container_client.list_blobs()
        temps = []
        for blob in blobs:
            blob_client = container_client.get_blob_client(blob)
            content = blob_client.download_blob().readall()
            data = json.loads(content)

            # Используем только данные с ключом "temperature"
            if "temperature" in data:
                temps.append(data["temperature"])

        if temps:
            return {"average_temperature": sum(temps) / len(temps)}
        return {"average_temperature": None}
    except Exception as e:
        logger.exception("Error in average_temperature")
        return {"error": str(e)}


@app.get("/api/device/alerts")
def low_soil_moisture_alert(threshold: int = 35):
    try:
        blobs = container_client.list_blobs()
        alerts = []
        for blob in blobs:
            blob_client = container_client.get_blob_client(blob)
            data = json.loads(blob_client.download_blob().readall())

            # Используем только данные с ключом "soilMoisture"
            if "soilMoisture" in data and data["soilMoisture"] < threshold:
                alerts.append(data)
        return {"alerts": alerts}
    except Exception as e:
        logger.exception("Error in low_soil_moisture_alert")
        return {"error": str(e)}



@app.get("/api/device/command")
def get_device_command():
    return irrigation_state
