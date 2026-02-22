import pandas as pd
import random

rows = []

for i in range(100):
    tenure = random.randint(1,72)
    monthly = round(random.uniform(40,110),2)
    total = round(monthly * tenure * random.uniform(0.9,1.05),2)

    rows.append({
        "gender": random.choice(["Male","Female"]),
        "SeniorCitizen": random.choice(["Yes","No"]),
        "Partner": random.choice(["Yes","No"]),
        "Dependents": random.choice(["Yes","No"]),
        "PhoneService": "Yes",
        "MultipleLines": random.choice(["Yes","No"]),
        "InternetService": random.choice(["DSL","Fiber optic"]),
        "OnlineSecurity": random.choice(["Yes","No"]),
        "OnlineBackup": random.choice(["Yes","No"]),
        "DeviceProtection": random.choice(["Yes","No"]),
        "TechSupport": random.choice(["Yes","No"]),
        "StreamingTV": random.choice(["Yes","No"]),
        "StreamingMovies": random.choice(["Yes","No"]),
        "tenure": tenure,
        "Contract": random.choice(["Month-to-month","One year","Two year"]),
        "PaperlessBilling": random.choice(["Yes","No"]),
        "PaymentMethod": random.choice([
            "Electronic check",
            "Credit card (automatic)",
            "Bank transfer (automatic)",
            "Mailed check"
        ]),
        "MonthlyCharges": monthly,
        "TotalCharges": total
    })

df = pd.DataFrame(rows)
df.to_csv("data/sample/test_churn_batch_100.csv", index=False)
print("Saved test_churn_batch.csv")