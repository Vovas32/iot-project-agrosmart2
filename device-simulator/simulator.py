import requests
import random
import time
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000/api/device/data"
COMMAND_URL = "http://127.0.0.1:8000/api/device/command"

while True:
    data = {
        "deviceId": "sensor-001",
        "temperature": round(random.uniform(15, 30), 2),
        "soilMoisture": random.randint(30, 70),
        "timestamp": datetime.utcnow().isoformat()
    }

    # Sending the data and receiving a command - - -
    try:
        # Send vvv
        requests.post(BACKEND_URL, json=data)
        print("Data sent:", data)

        # Get comman from backend vvv
        command = requests.get(COMMAND_URL).json()
        if command["irrigationOn"]:
            print("Irrigation system: ON")
        else:
            print("Irrigation system: OFF")

    except Exception as e:
        print("Error:", e)

    time.sleep(5)
