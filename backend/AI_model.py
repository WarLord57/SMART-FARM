import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib


# ============================================================
# MONGODB CONNECTION
# ============================================================

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "API"
COLLECTION_NAME = "sensor_data"

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


# ============================================================
# LOAD DATA FROM MONGODB
# ============================================================

data = list(collection.find())

if len(data) < 100:
    raise ValueError(
        f"Only {len(data)} records found. "
        "You need substantially more historical data to train the model."
    )

df = pd.DataFrame(data)


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df = df.rename(columns={
    "humidty": "humidity"
})


# ============================================================
# CONVERT DATE + TIME
# ============================================================

df["datestamp"] = pd.to_datetime(df["datestamp"])

df["timestamp"] = pd.to_timedelta(
    df["timestamp"].astype(str)
)

df["datetime"] = (
    df["datestamp"].dt.normalize()
    + df["timestamp"]
)

df = df.sort_values("datetime").reset_index(drop=True)


# ============================================================
# CONVERT SENSOR VALUES TO NUMERIC
# ============================================================

numeric_columns = [
    "temperature",
    "humidity",
    "moisture",
    "moisture_p",
    "component1"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# Remove invalid rows
df = df.dropna(
    subset=[
        "temperature",
        "humidity",
        "moisture",
        "moisture_p",
        "datetime"
    ]
)


# ============================================================
# DEFINE WATERING THRESHOLD
# ============================================================

WATERING_THRESHOLD = 30


# ============================================================
# CREATE TARGET
# ============================================================

def calculate_hours_until_watering(df):

    target = []

    for i in range(len(df)):

        current_time = df.loc[i, "datetime"]

        future_rows = df.iloc[i + 1:]

        watering_time = None

        for _, future in future_rows.iterrows():

            if future["moisture_p"] <= WATERING_THRESHOLD:

                watering_time = future["datetime"]
                break

        if watering_time is None:
            target.append(np.nan)
        else:
            hours = (
                watering_time - current_time
            ).total_seconds() / 3600

            target.append(hours)

    return target


df["hours_until_watering"] = calculate_hours_until_watering(df)


# Remove rows where we don't know when watering occurred
df = df.dropna(
    subset=["hours_until_watering"]
)


# ============================================================
# FEATURES
# ============================================================

features = [
    "temperature",
    "humidity",
    "moisture",
    "moisture_p"
]

X = df[features]

y = df["hours_until_watering"]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ============================================================
# TRAIN MODEL
# ============================================================

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)


# ============================================================
# EVALUATE
# ============================================================

predictions = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

print("--------------------------------")
print("MODEL RESULTS")
print("--------------------------------")

print(f"Records: {len(df)}")
print(f"MAE: {mae:.2f} hours")
print(f"RMSE: {rmse:.2f} hours")


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    model,
    "soil_watering_model.pkl"
)

print()
print("Model saved as:")
print("soil_watering_model.pkl")