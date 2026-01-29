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
# Azure Blob Storage      vvvv  
# --------------------
AZURE_CONNECTION_STRING = "  "    #  <---  KEY HERE
CONTAINER_NAME = "iot-data"

blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service.get_container_client(CONTAINER_NAME)

# Try to make a container 
try:
    container_client.create_container()
    logger.info(f"Blob container '{CONTAINER_NAME}' created.")
except Exception:
    logger.info(f"Blob container '{CONTAINER_NAME}' already exists.")

# --------------------
# In-memory device state
# --------------------
irrigation_state = {"irrigationOn": False}
thresholds = {"soilMoisture": 40}

# --------------------
# Helper functions
# --------------------
def read_all_messages_from_blobs():
    blobs = container_client.list_blobs()
    all_messages = []

    for blob in blobs:
        try:
            blob_client = container_client.get_blob_client(blob)
            content = blob_client.download_blob().readall().decode('utf-8')
            for line in content.splitlines():
                if not line.strip():
                    continue
                data = json.loads(line)
                if isinstance(data, dict) and "Body" in data:
                    all_messages.append(data["Body"])
                elif isinstance(data, dict):
                    all_messages.append(data)
        except Exception:
            logger.warning(f"Skipping invalid blob: {blob.name}")
    return all_messages

def save_blob(data: dict):
    blob_name = f"{datetime.utcnow().isoformat()}.json"
    container_client.upload_blob(
        blob_name,
        json.dumps(data),
        overwrite=True,
        content_settings=ContentSettings(content_type="application/json")
    )
    logger.info(f"Saved blob {blob_name}")

# --------------------
# API Endpoints
# --------------------
@app.post("/api/device/data")
def receive_data(data: dict):
    global irrigation_state
    try:
        sm = data.get("soilMoisture", 100)
        irrigation_state["irrigationOn"] = sm < thresholds["soilMoisture"]
        save_blob(data)
        return {"status": "ok", "irrigationOn": irrigation_state["irrigationOn"]}
    except Exception as e:
        logger.exception("Error receiving device data")
        return {"error": str(e)}

@app.get("/api/device/data")
def get_data():
    return read_all_messages_from_blobs()

@app.get("/api/device/average")
def average_temperature():
    data = read_all_messages_from_blobs()
    temps = [d["temperature"] for d in data if isinstance(d, dict) and "temperature" in d]
    return {"average_temperature": sum(temps)/len(temps) if temps else None}

@app.get("/api/device/average-moisture")
def average_moisture():
    data = read_all_messages_from_blobs()
    moistures = [d["soilMoisture"] for d in data if isinstance(d, dict) and "soilMoisture" in d]
    return {"average_soilMoisture": sum(moistures)/len(moistures) if moistures else None}

@app.get("/api/device/alerts")
def low_soil_moisture_alert(threshold: int = 35):
    data = read_all_messages_from_blobs()
    alerts = [d for d in data if isinstance(d, dict) and "soilMoisture" in d and d["soilMoisture"] < threshold]
    return {"alerts": alerts}

@app.get("/api/device/command")
def get_device_command():
    return irrigation_state

@app.get("/api/device/thresholds")
def get_thresholds():
    return thresholds

@app.post("/api/device/set-thresholds")
def set_thresholds(new_threshold: dict):
    thresholds.update(new_threshold)
    return {"status": "ok", "thresholds": thresholds}

@app.get("/api/device/stats")
def device_stats():
    data = read_all_messages_from_blobs()
    temps = [d["temperature"] for d in data if isinstance(d, dict) and "temperature" in d]
    moistures = [d["soilMoisture"] for d in data if isinstance(d, dict) and "soilMoisture" in d]

    return {
        "count": len(data),
        "temperature": {
            "average": sum(temps)/len(temps) if temps else None,
            "min": min(temps) if temps else None,
            "max": max(temps) if temps else None
        },
        "soilMoisture": {
            "average": sum(moistures)/len(moistures) if moistures else None,
            "min": min(moistures) if moistures else None,
            "max": max(moistures) if moistures else None
        }
    }

@app.get("/")
def root():
    return {"message": "SmartAgro backend is online!"}
