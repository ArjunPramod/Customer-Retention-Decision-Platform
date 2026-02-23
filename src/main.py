from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any
from src.retention_engine import predict_customer, predict_batch
import pandas as pd

from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timezone
import uuid
import os

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

app = FastAPI(title="Customer Retention API", version="1.0")

# --------------------------------------------------
# Request Schema
# --------------------------------------------------

class CustomerInput(BaseModel):
    gender: str
    SeniorCitizen: str
    Partner: str
    Dependents: str
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    tenure: int
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

# --------------------------------------------------
# Prediction Endpoint
# --------------------------------------------------

@app.post("/predict")
def predict(customer: CustomerInput):

    result = predict_customer(customer.model_dump())

    payload = {
        "input": customer.model_dump(),
        "churn_probability": result["churn_probability"],
        "urgency": result["urgency"],
        "cluster": result["cluster"],
        "persona": result["persona"],
        "recommended_actions": result["recommended_actions"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    supabase.table("predictions").insert(payload).execute()

    return result

@app.post("/predict_batch")
async def predict_batch_endpoint(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)

    results = predict_batch(df)

    batch_id = str(uuid.uuid4())

    records = []

    for _, row in results.iterrows():
        records.append({
            "batch_id": batch_id,
            "input": row.drop([
                "row_id",
                "churn_probability",
                "urgency",
                "cluster",
                "persona",
                "recommended_actions"
            ]).to_dict(),
            "churn_probability": row["churn_probability"],
            "urgency": row["urgency"],
            "cluster": int(row["cluster"]),
            "persona": row["persona"],
            "recommended_actions": row["recommended_actions"],
            "created_at": datetime.now(timezone.utc).isoformat()
        })

    supabase.table("predictions").insert(records).execute()

    return results.to_dict(orient="records")

@app.get("/history")
def get_prediction_history():

    response = (
        supabase
        .table("predictions")
        .select("*")
        .order("created_at", desc=True)
        .limit(500)
        .execute()
    )

    return response.data

@app.get("/history_count")
def get_prediction_count():

    resp = supabase.table("predictions").select("id", count="exact").execute()

    return {"total": resp.count}