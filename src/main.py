from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any
from src.retention_engine import predict_customer, predict_batch
import pandas as pd

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

    return result

@app.post("/predict_batch")
async def predict_batch_endpoint(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)

    results = predict_batch(df)

    return results.to_dict(orient="records")