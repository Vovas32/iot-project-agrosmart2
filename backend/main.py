from fastapi import FastAPI
from azure.storage.blob import BlobServiceClient, ContentSettings
import json
from datetime import datetime
import logging

# --------------------
# Logging
# --------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------
# App
# --------------------
app = FastAPI(
    title="SmartAgro IoT Backend",
    description="Backend service for Smart Agriculture IoT system",
    version="1.0.0"
)

# --------------------
# Azure Blob Storage
# --------------------
# IMPORTANT: remove or replace this value before pushing to public repository
AZURE_CONNECTION_STRING = "   "

CONTAINER_NAME = "iot-data"

blob_service = BlobServiceClient.from_connection_string(
    AZURE_CONNECTION_STRING
)
container_client = blob_service.get_container_client(CONTAINER_NAME)

# Create container if not exists
try:
    container_client.create_container()
    logger.info("Blob container created")
except Exception:
    logger.info("Blob container already exists")

# --------------------
# In-memory device state
# --------------------
irrigation_state = {"irrigationOn": False}

# --------------------
# Helper functions
# --------------------
def read_all_valid_blobs():
    """
    Reads all blobs from the container.
    Skips invalid or corrupted JSON files.
    """
    blobs = container_client.list_blobs()
    result = []

    for blob in blobs:
        try:
            blob_client = container_client.get_blob_client(blob)
            content = blob_client.download_blob().readall()
            result.append(json.loads(content))
        except Exception:
            logger.warning(f"Skipping invalid blob: {blob.name}")

    return result


def save_blob(data: dict):
    """
    Saves sensor data as a JSON blob.
    """
    blob_name = f"{datetime.utcnow().isoformat()}.json"
    container_client.upload_blob(
        blob_name,
        json.dumps(data),
        overwrite=True,
        content_settings=ContentSettings(
            content_type="application/json"
        )
    )


# --------------------
# API Endpoints
# --------------------
@app.post("/api/device/data")
def receive_data(data: dict):
    """
    Receives data from IoT device (or simulator).
    Applies irrigation logic and stores data in Blob Storage.
    """
    global irrigation_state

    try:
        # Auto irrigation logic
        if data.get("soilMoisture", 100) < 40:
            irrigation_state["irrigationOn"] = True
        else:
            irrigation_state["irrigationOn"] = False

        save_blob(data)

        return {
            "status": "ok",
            "irrigationOn": irrigation_state["irrigationOn"]
        }

    except Exception as e:
        logger.exception("Error while receiving device data")
        return {"error": str(e)}


@app.get("/api/device/data")
def get_data():
    """
    Returns all valid stored sensor data.
    """
    return read_all_valid_blobs()


@app.get("/api/device/average")
def average_temperature():
    """
    Calculates average temperature from stored data.
    """
    data = read_all_valid_blobs()
    temps = [d["temperature"] for d in data if "temperature" in d]

    if temps:
        return {"average_temperature": sum(temps) / len(temps)}

    return {"average_temperature": None}


@app.get("/api/device/alerts")
def low_soil_moisture_alert(threshold: int = 35):
    """
    Returns alerts for low soil moisture.
    """
    data = read_all_valid_blobs()

    alerts = [
        d for d in data
        if "soilMoisture" in d and d["soilMoisture"] < threshold
    ]

    return {"alerts": alerts}


@app.get("/api/device/command")
def get_device_command():
    """
    Returns the current irrigation command for the device.
    """
    return irrigation_state

