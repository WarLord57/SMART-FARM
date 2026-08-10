import os
from pathlib import Path
from datetime import date, time, datetime, timedelta
from typing import Optional

import joblib
import pandas as pd
import pymongo
import requests

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Smart Irrigation API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

# Add your Vercel frontend URL here later.
# For development, localhost:5173 is enough.

origins = [
    "http://localhost:5173",
]

# Optional frontend URL from Vercel environment variable
FRONTEND_URL = os.getenv("FRONTEND_URL")

if FRONTEND_URL:
    origins.append(FRONTEND_URL)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

MONGO_URI = os.getenv("MONGO_URI")

MONGO_DATABASE = os.getenv(
    "MONGO_DATABASE",
    "API"
)

MONGO_COLLECTION = os.getenv(
    "MONGO_COLLECTION",
    "sensor_data"
)

ESP8266_URL = os.getenv(
    "ESP8266_URL",
    ""
)


# ============================================================
# MONGODB
# ============================================================

mongo_client = None
sensor_collection = None


def get_database():
    """
    Create MongoDB connection when needed.

    We don't connect to MongoDB during module import.
    This prevents MongoDB problems from killing the
    entire FastAPI deployment.
    """

    global mongo_client
    global sensor_collection

    if sensor_collection is not None:
        return sensor_collection

    if not MONGO_URI:
        raise RuntimeError(
            "MONGO_URI environment variable is not configured."
        )

    mongo_client = pymongo.MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    # Test connection
    mongo_client.admin.command("ping")

    database = mongo_client[MONGO_DATABASE]

    sensor_collection = database[MONGO_COLLECTION]

    return sensor_collection


# ============================================================
# MACHINE LEARNING MODEL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "soil_watering_model.pkl"

model = None


def get_model():
    """
    Load the ML model only when it is actually needed.
    """

    global model

    if model is not None:
        return model

    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"ML model not found: {MODEL_PATH}"
        )

    try:
        model = joblib.load(MODEL_PATH)
    except Exception as error:
        raise RuntimeError(
            f"Could not load ML model: {error}"
        )

    return model


def predict_watering_time(
    temperature: float,
    humidity: float,
    moisture: float,
    moisture_p: float
) -> float:

    ml_model = get_model()

    input_data = pd.DataFrame([
        {
            "temperature": temperature,
            "humidity": humidity,
            "moisture": moisture,
            "moisture_p": moisture_p
        }
    ])

    prediction = ml_model.predict(input_data)[0]

    return round(float(prediction), 2)


# ============================================================
# PYDANTIC MODELS
# ============================================================

class SensorData(BaseModel):

    name: str

    temperature: float

    humidity: float

    moisture: float

    moisture_p: float

    status_moisture: Optional[str] = None

    component1: int

    datestamp: date

    timestamp: time


class FilterValue(BaseModel):

    start_datestamp: date = Field(
        default_factory=date.today
    )

    end_datestamp: date = Field(
        default_factory=date.today
    )

    timestamp: Optional[time] = None

    frequency: int = 0


class SwitchValue(BaseModel):

    auto: bool = False

    number: int = 0


class PredictionData(BaseModel):

    temperature: float

    humidity: float

    moisture: float

    moisture_p: float


# ============================================================
# HELPER
# ============================================================

def serialize_document(document):

    if "_id" in document:
        document["_id"] = str(document["_id"])

    return document


# ============================================================
# BASIC TEST ENDPOINTS
# ============================================================

@app.get("/")
async def root():

    return {
        "message": "Smart Irrigation API is running"
    }


@app.get("/api/test")
async def test():

    return {
        "message": "FastAPI is working on Vercel"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
async def health():

    result = {
        "api": "ok",
        "mongodb": "not tested",
        "model": "not tested"
    }

    # Test MongoDB
    try:

        collection = get_database()

        collection.database.client.admin.command("ping")

        result["mongodb"] = "connected"

    except Exception as error:

        result["mongodb"] = f"error: {str(error)}"


    # Test model
    try:

        get_model()

        result["model"] = "loaded"

    except Exception as error:

        result["model"] = f"error: {str(error)}"


    return result


# ============================================================
# MONGODB TEST
# ============================================================

@app.get("/api/mongo-test")
async def mongo_test():

    try:

        collection = get_database()

        collection.database.client.admin.command("ping")

        return {
            "success": True,
            "message": "MongoDB Atlas connection successful"
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"MongoDB connection failed: {str(error)}"
        )


# ============================================================
# POST SENSOR DATA
# ============================================================

@app.post("/svc/api/")
async def post_data(sensor_data: SensorData):

    try:

        collection = get_database()

        document = {
            "name": sensor_data.name,

            "temperature": sensor_data.temperature,

            "humidity": sensor_data.humidity,

            "moisture": sensor_data.moisture,

            "moisture_p": sensor_data.moisture_p,

            "status_moisture": sensor_data.status_moisture,

            "component1": sensor_data.component1,

            "datestamp": sensor_data.datestamp.isoformat(),

            "timestamp": sensor_data.timestamp.isoformat(),

            "created_at": datetime.utcnow()
        }

        result = collection.insert_one(document)

        return {
            "success": True,
            "message": "Data posted successfully",
            "id": str(result.inserted_id)
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save sensor data: {str(error)}"
        )


# ============================================================
# GET ALL SENSOR DATA
# ============================================================

@app.get("/svc/api/")
async def get_data():

    try:

        collection = get_database()

        documents = collection.find(
            {}
        ).sort(
            "_id",
            pymongo.DESCENDING
        )

        data = []

        for document in documents:

            data.append(
                serialize_document(document)
            )

        return data

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve sensor data: {str(error)}"
        )


# ============================================================
# AGGREGATED SENSOR DATA
# ============================================================

@app.post("/svc/api/agg")
async def get_agg_data(filter_value: FilterValue):

    try:

        collection = get_database()

        documents = list(
            collection.find({})
        )

        if not documents:

            return {
                "message": "No data to retrieve"
            }

        df = pd.DataFrame(documents)

        if df.empty:

            return {
                "message": "No data to retrieve"
            }

        # Convert datestamp
        df["datestamp"] = pd.to_datetime(
            df["datestamp"],
            errors="coerce"
        )

        # Remove invalid dates
        df = df.dropna(
            subset=["datestamp"]
        )

        # Date filtering
        start_date = pd.Timestamp(
            filter_value.start_datestamp
        )

        end_date = (
            pd.Timestamp(
                filter_value.end_datestamp
            )
            + pd.Timedelta(days=1)
            - pd.Timedelta(seconds=1)
        )

        df = df[
            (df["datestamp"] >= start_date)
            &
            (df["datestamp"] <= end_date)
        ]

        if df.empty:

            return {
                "message": "No data to retrieve"
            }

        # Numeric columns
        numeric_columns = [
            "temperature",
            "humidity",
            "moisture",
            "moisture_p",
            "component1"
        ]

        existing_columns = [
            column
            for column in numeric_columns
            if column in df.columns
        ]

        averages = (
            df[existing_columns]
            .apply(pd.to_numeric, errors="coerce")
            .mean()
            .to_dict()
        )

        return averages

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Aggregation failed: {str(error)}"
        )


# ============================================================
# LIVE FEED
# ============================================================

@app.get("/svc/api/livefeed/")
async def get_live_feed():

    try:

        collection = get_database()

        thirty_seconds_ago = (
            datetime.utcnow()
            - timedelta(seconds=30)
        )

        documents = list(
            collection.find({})
            .sort("_id", pymongo.DESCENDING)
            .limit(20)
        )

        if not documents:

            return {
                "message": "Smart Irrigation system offline"
            }

        df = pd.DataFrame(documents)

        if df.empty:

            return {
                "message": "Smart Irrigation system offline"
            }

        # Make timestamp into datetime
        if "timestamp" in df.columns:

            df["timestamp_dt"] = pd.to_datetime(
                df["timestamp"],
                format="%H:%M:%S",
                errors="coerce"
            )

        # Get latest record
        latest = df.iloc[0]

        temperature = float(
            latest["temperature"]
        )

        humidity = float(
            latest["humidity"]
        )

        moisture = float(
            latest["moisture"]
        )

        moisture_p = float(
            latest["moisture_p"]
        )

        status = str(
            latest.get(
                "status_moisture",
                ""
            )
        )

        component = int(
            latest.get(
                "component1",
                0
            )
        )

        # ML prediction
        hours = predict_watering_time(
            temperature=temperature,
            humidity=humidity,
            moisture=moisture,
            moisture_p=moisture_p
        )

        return {
            "temperature": temperature,
            "humidity": humidity,
            "moisture": moisture,
            "moisture_p": moisture_p,
            "status": status,
            "component": component,
            "hours": hours
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Live feed failed: {str(error)}"
        )


# ============================================================
# ML PREDICTION
# ============================================================

@app.post("/api/predict")
async def predict(data: PredictionData):

    try:

        hours = predict_watering_time(
            temperature=data.temperature,
            humidity=data.humidity,
            moisture=data.moisture,
            moisture_p=data.moisture_p
        )

        return {
            "hours_until_watering": hours
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}"
        )


# ============================================================
# ESP8266 PUMP SWITCH
# ============================================================

@app.post("/api/switch/")
async def switch_pump(
    switch_value: SwitchValue
):

    if not ESP8266_URL:

        raise HTTPException(
            status_code=500,
            detail="ESP8266_URL is not configured"
        )

    data = {
        "auto": switch_value.auto,
        "number": switch_value.number
    }

    try:

        response = requests.post(
            ESP8266_URL,
            json=data,
            timeout=5
        )

        response.raise_for_status()

        return {
            "success": True,
            "response": response.text
        }

    except requests.exceptions.RequestException as error:

        raise HTTPException(
            status_code=502,
            detail=f"ESP8266 request failed: {str(error)}"
        )