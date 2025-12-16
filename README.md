SmartAgro IoT Project

Description:
SmartAgro is an IoT system for smart agriculture. The system collects sensor data (soil moisture, temperature), stores it in the cloud (Azure Blob Storage), analyzes it, and automatically manages the irrigation system.

Technologies:

Backend: FastAPI (Python)

Device Simulator: Python + requests

Cloud Storage: Azure Blob Storage

REST API

Postman Collection for API testing

1. Repository Structure (my parts)
smartagro-iot/
├── backend/
│   └── main.py        # Backend API (FastAPI)
├── device-simulator/
│   └── simulator.py   # IoT Device Simulator
├── postman/
│   └── docs/
│       ├── architecture-c1-context.drawio
│       └── architecture-c2-container.drawio
│   └── collection.json  # Postman collection
└── README.md

2. Installation

Clone the repository and go to the project folder:

# Clone the repository
git clone <your-repo-url>

# Go to the project folder
cd smartagro-iot


Create and activate a virtual environment:

# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / Mac
python -m venv venv
source venv/bin/activate


Install dependencies:

# Install Python libraries
pip install fastapi uvicorn requests azure-storage-blob


Configure Azure:

Create a Storage Account in Azure.

Get the Connection String.

Insert it into backend/main.py:

# Do NOT store this secret in a public repository!
AZURE_CONNECTION_STRING = "<your_connection_string>"
CONTAINER_NAME = "iot-data"


The backend will automatically create the container if it does not exist.

3. Running the Project
3.1 Backend
cd backend
uvicorn main:app --reload


API will be available at: http://127.0.0.1:8000/docs

3.2 Device Simulator
cd device-simulator
python simulator.py


The simulator:

Sends data every 5 seconds

Receives irrigation commands

Stop the simulator with Ctrl + C

4. REST API
Endpoint	Method	Description
/api/device/data	POST	Send sensor data
/api/device/data	GET	Get all data
/api/device/average	GET	Average temperature
/api/device/alerts	GET	Low soil moisture alerts
/api/device/command	GET	Irrigation command (ON/OFF)
5. Postman Collection

File: postman/collection.json

Example requests:

POST /api/device/data

{
  "deviceId": "sensor-001",
  "temperature": 25.5,
  "soilMoisture": 45,
  "timestamp": "2025-12-15T15:30:00"
}


GET /api/device/data — get all data
GET /api/device/alerts?threshold=35 — get alerts
GET /api/device/average — average temperature
GET /api/device/command — irrigation command

6. Architecture (C4 Model)
C1 — System Context

User / Farmer: monitoring and controlling the system

IoT Device: sensors and actuator

SmartAgro IoT System: backend + storage

Azure Cloud: data storage

Connections:

IoT Device → SmartAgro IoT System (POST sensor data / GET command)

User → SmartAgro IoT System (monitoring / control)

SmartAgro IoT System → Azure Cloud (data storage)

C2 — Container

IoT Device Simulator: sensor + irrigation simulation

Backend API (FastAPI): business logic, REST API, data processing, irrigation command

Azure Blob Storage: JSON data storage

User / Farmer: interacts via REST API

Connections:

IoT → Backend API (POST / GET)

Backend API → Azure Blob Storage (SDK call, store telemetry)

User → Backend API (GET data / alerts / statistics)

7. Business Logic & User Stories

Automatic Irrigation:

If soilMoisture < 40 → irrigation ON

If soilMoisture ≥ 40 → irrigation OFF

User Stories:

User	Goal	Reason
Farmer	Receive sensor updates	Monitor crops in real-time
Farmer	Automatic irrigation for dry soil	Efficient watering and water savings
Business Owner	Access historical data	Analyze trends and make decisions
Developer	Clear REST API	Easy integration with other applications
8. Azure Pricing

Using Blob Storage (Hot Tier)

Estimated cost: $1.15/month (demo scenario: 1 IoT device, small data volume)

Azure Pricing Calculator - https://azure.com/e/6605eb5e83084a668ff0801697f022c4

9. Testing

Start the backend and simulator

Open Swagger UI: http://127.0.0.1:8000/docs

Run requests from Postman collection

Check:

Data is sent correctly

Irrigation commands are received (ON/OFF)

Average and alert endpoints work

10. Author / Contact

Name: Volodymyr Sadchyi
Project completed individually