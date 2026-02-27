import pandas as pd
import numpy as np

np.random.seed(42)

N = 1000   # how many rows you want

# -----------------------
# 1. CHURN DISTRIBUTION
# -----------------------

churn_probs = {"No": 0.734, "Yes": 0.266}

# -----------------------
# 2. CATEGORICAL WEIGHTS
# -----------------------

gender = {"Male": 3549, "Female": 3483}
partner = {"No": 3639, "Yes": 3393}
dependents = {"No": 4933, "Yes": 2099}
paperless = {"Yes": 4168, "No": 2864}

contract_by_churn = {
    "No": {"Month-to-month": 0.573, "One year": 0.314, "Two year": 0.113},
    "Yes": {"Month-to-month": 0.427, "One year": 0.113, "Two year": 0.028}
}

internet_by_churn = {
    "No": {"DSL": 0.810, "Fiber optic": 0.581, "No": 0.926},
    "Yes": {"DSL": 0.190, "Fiber optic": 0.419, "No": 0.074}
}

payment_by_churn = {
    "No": {
        "Electronic check": 0.547,
        "Mailed check": 0.808,
        "Bank transfer (automatic)": 0.833,
        "Credit card (automatic)": 0.847
    },
    "Yes": {
        "Electronic check": 0.453,
        "Mailed check": 0.192,
        "Bank transfer (automatic)": 0.167,
        "Credit card (automatic)": 0.153
    }
}

senior_by_churn = {
    "No": {"No": 0.763, "Yes": 0.237},
    "Yes": {"No": 0.583, "Yes": 0.417}
}

# -----------------------
# 3. NUMERIC STATS
# -----------------------

numeric_stats = {
    "No": {
        "tenure": (37.65, 24.08),
        "MonthlyCharges": (61.31, 31.09)
    },
    "Yes": {
        "tenure": (17.98, 19.53),
        "MonthlyCharges": (74.44, 24.67)
    }
}

# -----------------------
# HELPERS
# -----------------------

def weighted_choice(d):
    return np.random.choice(list(d.keys()), p=np.array(list(d.values()))/sum(d.values()))

rows = []

# -----------------------
# GENERATION LOOP
# -----------------------

for _ in range(N):

    churn = weighted_choice(churn_probs)

    tenure = max(1, min(72, int(np.random.normal(*numeric_stats[churn]["tenure"]))))

    monthly = round(max(18, np.random.normal(*numeric_stats[churn]["MonthlyCharges"])), 2)

    total = round(monthly * tenure * np.random.uniform(0.9,1.05), 2)

    row = {
        "Churn": churn,
        "gender": weighted_choice(gender),
        "SeniorCitizen": weighted_choice(senior_by_churn[churn]),
        "Partner": weighted_choice(partner),
        "Dependents": weighted_choice(dependents),
        "PhoneService": "Yes",
        "MultipleLines": np.random.choice(["Yes","No"], p=[0.42,0.58]),
        "InternetService": weighted_choice(internet_by_churn[churn]),
        "OnlineSecurity": np.random.choice(["Yes","No"], p=[0.29,0.71]),
        "OnlineBackup": np.random.choice(["Yes","No"], p=[0.34,0.66]),
        "DeviceProtection": np.random.choice(["Yes","No"], p=[0.34,0.66]),
        "TechSupport": np.random.choice(["Yes","No"], p=[0.29,0.71]),
        "StreamingTV": np.random.choice(["Yes","No"], p=[0.38,0.62]),
        "StreamingMovies": np.random.choice(["Yes","No"], p=[0.38,0.62]),
        "Contract": weighted_choice(contract_by_churn[churn]),
        "PaperlessBilling": weighted_choice(paperless),
        "PaymentMethod": weighted_choice(payment_by_churn[churn]),
        "tenure": tenure,
        "MonthlyCharges": round(monthly,2),
        "TotalCharges": total
    }

    rows.append(row)

df = pd.DataFrame(rows)

df.to_csv("../data/sample/test_churn_batch_1000.csv", index=False)

print("Saved ../data/sample/test_churn_batch_1000.csv")
