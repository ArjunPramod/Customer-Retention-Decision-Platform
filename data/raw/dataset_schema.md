## Dataset Summary
**Dataset Name:** Telco Customer Churn (IBM Sample Data Set)  
**Domain:** Telecom / Customer Retention  
**Rows:** 7,043 customers  
**Columns:** 20 features + 1 target  
**Granularity:** One row per customer  
**Target Variable:** Churn  
**Prediction Task:** Binary classification (churn vs non-churn)

## Target Variable Definition
**Churn Definition:**  
The `Churn` variable indicates whether a customer left the service in the last month.

- Yes → Customer churned  
- No → Customer retained

## Feature Metadata
| Feature Name        | Data Type     | Description |
|--------------------|---------------|-------------|
| customerID         | Identifier    | Unique customer identifier |
| gender             | Categorical   | Customer gender (Male, Female) |
| SeniorCitizen      | Binary        | Whether the customer is a senior citizen (1, 0) |
| Partner            | Binary        | Whether the customer has a partner (Yes, No) |
| Dependents         | Binary        | Whether the customer has dependents (Yes, No) |
| tenure             | Numerical     | Number of months the customer has stayed with the company |
| PhoneService       | Binary        | Whether the customer has phone service (Yes, No) |
| MultipleLines      | Categorical   | Whether the customer has multiple lines (Yes, No, No phone service) |
| InternetService    | Categorical   | Internet service type (DSL, Fiber optic, No) |
| OnlineSecurity     | Categorical   | Whether the customer has online security (Yes, No, No internet service) |
| OnlineBackup       | Categorical   | Whether the customer has online backup (Yes, No, No internet service) |
| DeviceProtection   | Categorical   | Whether the customer has device protection (Yes, No, No internet service) |
| TechSupport        | Categorical   | Whether the customer has tech support (Yes, No, No internet service) |
| StreamingTV        | Categorical   | Whether the customer has streaming TV (Yes, No, No internet service) |
| StreamingMovies    | Categorical   | Whether the customer has streaming movies (Yes, No, No internet service) |
| Contract           | Categorical   | Contract type (Month-to-month, One year, Two year) |
| PaperlessBilling   | Binary        | Whether the customer uses paperless billing (Yes, No) |
| PaymentMethod      | Categorical   | Payment method (Electronic check, Mailed check, Bank transfer (automatic), Credit card (automatic)) |
| MonthlyCharges     | Numerical     | Monthly charges billed to the customer |
| TotalCharges       | Numerical     | Total charges billed over the customer lifetime |
| Churn              | Binary (Target) | Whether the customer churned (Yes, No) |

## Assumptions and Scope
- Each row represents an independent customer
- No explicit temporal sequence is provided beyond customer tenure
- The dataset represents a snapshot of churn behavior
- Churn is treated as a binary outcome, not a time-to-event problem