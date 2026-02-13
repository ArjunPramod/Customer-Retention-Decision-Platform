import gradio as gr
import requests

FASTAPI_URL = "http://localhost:8000"

# ------------------------------------------------
# Dependency Logic
# ------------------------------------------------

def handle_phone_service(phone):
    if phone == "No":
        return gr.update(
            choices=["No phone service"],
            value="No phone service",
            interactive=False
        )
    else:
        return gr.update(
            choices=["Yes", "No"],
            value="No",
            interactive=True
        )


def handle_internet_service(internet):
    updates = []

    if internet == "No":
        for _ in range(6):
            updates.append(
                gr.update(
                    choices=["No internet service"],
                    value="No internet service",
                    interactive=False
                )
            )
    else:
        for _ in range(6):
            updates.append(
                gr.update(
                    choices=["Yes", "No"],
                    value="No",
                    interactive=True
                )
            )

    return updates


# ------------------------------------------------
# FastAPI Calls
# ------------------------------------------------

def predict_single(*inputs):

    payload = {
        "gender": inputs[0],
        "SeniorCitizen": inputs[1],
        "Partner": inputs[2],
        "Dependents": inputs[3],
        "PhoneService": inputs[4],
        "MultipleLines": inputs[5],
        "InternetService": inputs[6],
        "OnlineSecurity": inputs[7],
        "OnlineBackup": inputs[8],
        "DeviceProtection": inputs[9],
        "TechSupport": inputs[10],
        "StreamingTV": inputs[11],
        "StreamingMovies": inputs[12],
        "tenure": inputs[13],
        "Contract": inputs[14],
        "PaperlessBilling": inputs[15],
        "PaymentMethod": inputs[16],
        "MonthlyCharges": inputs[17],
        "TotalCharges": inputs[18],
    }

    r = requests.post(f"{FASTAPI_URL}/predict", json=payload)
    result = r.json()

    return (
        result["risk_level"],
        result["churn_probability"],
        result["segment"],
        result["expected_loss"],
        result["retention_cost"],
        result["decision"],
        result["retention_action"],
        result["explanation"],
    )


def batch_predict(file):
    r = requests.post(
        f"{FASTAPI_URL}/batch_predict",
        files={"file": open(file.name, "rb")}
    )

    out_path = "batch_results.csv"

    with open(out_path, "wb") as f:
        f.write(r.content)

    return out_path


# ------------------------------------------------
# UI
# ------------------------------------------------

with gr.Blocks(title="Telecom Churn System") as demo:

    gr.Markdown("""
        # 📊 Telecom Customer Retention Decision Platform  
        ### Predict churn risk, segment customers, and generate cost-aware retention actions
        """)
    
    with gr.Tabs():

        # ==================================================
        # SINGLE CUSTOMER
        # ==================================================
        with gr.Tab("Single Customer"):

            with gr.Row():

                # LEFT COLUMN
                with gr.Column():

                    with gr.Accordion("👤 Demographics", open=True):
                        gender = gr.Dropdown(["Female", "Male"], label="Gender")
                        SeniorCitizen = gr.Radio(["Yes", "No"], label="Senior Citizen")
                        Partner = gr.Radio(["Yes", "No"], label="Partner")
                        Dependents = gr.Radio(["Yes", "No"], label="Dependents")

                    with gr.Accordion("📞 Phone Services", open=False):
                        PhoneService = gr.Radio(["Yes", "No"], label="Phone Service")

                        # IMPORTANT: clean initial state
                        MultipleLines = gr.Dropdown(
                            ["Yes", "No"],
                            label="Multiple Lines"
                        )

                    with gr.Accordion("🌐 Internet & Add-On Services", open=False):
                        InternetService = gr.Dropdown(
                            ["DSL", "Fiber optic", "No"],
                            label="Internet Service"
                        )

                        # IMPORTANT: clean initial state (no "No internet service")
                        OnlineSecurity = gr.Dropdown(["Yes", "No"], label="Online Security")
                        OnlineBackup = gr.Dropdown(["Yes", "No"], label="Online Backup")
                        DeviceProtection = gr.Dropdown(["Yes", "No"], label="Device Protection")
                        TechSupport = gr.Dropdown(["Yes", "No"], label="Tech Support")
                        StreamingTV = gr.Dropdown(["Yes", "No"], label="Streaming TV")
                        StreamingMovies = gr.Dropdown(["Yes", "No"], label="Streaming Movies")

                    with gr.Accordion("🧾 Account Information", open=False):
                        tenure = gr.Number(label="Tenure")
                        Contract = gr.Dropdown(
                            ["Month-to-month", "One year", "Two year"],
                            label="Contract"
                        )
                        PaperlessBilling = gr.Radio(["Yes", "No"], label="Paperless billing")
                        PaymentMethod = gr.Dropdown(
                            [
                                "Bank transfer (automatic)",
                                "Credit card (automatic)",
                                "Electronic check",
                                "Mailed check"
                            ],
                            label="Payment Method"
                        )

                    with gr.Accordion("💰 Financials", open=False):
                        MonthlyCharges = gr.Number(label="Monthly Charges")
                        TotalCharges = gr.Number(label="Total Charges")

                    predict_btn = gr.Button("Predict Customer")

                # RIGHT COLUMN
                with gr.Column():

                    with gr.Group():
                        gr.Markdown("### 📈 Risk Summary")
                        risk = gr.Label(label="Churn Risk")
                        prob = gr.Number(label="Churn Probability")

                    with gr.Group():
                        gr.Markdown("### 👤 Customer Segment")
                        segment = gr.Textbox(show_label=False)

                    with gr.Group():
                        gr.Markdown("### 💰 Economic Impact")
                        with gr.Row():
                            loss = gr.Number(label="Expected Loss ($)")
                            cost = gr.Number(label="Retention Cost ($)")

                    with gr.Group():
                        gr.Markdown("### 🎯 Retention Decision")
                        decision = gr.Label(label="Final Decision")
                        action = gr.Textbox(label="Recommended Action")

                    with gr.Group():
                        gr.Markdown("### 🧠 Why This Decision?")
                        explanation = gr.Textbox(lines=3, show_label=False)


            # Dependency callbacks
            PhoneService.change(handle_phone_service, PhoneService, MultipleLines)

            InternetService.change(
                handle_internet_service,
                InternetService,
                [
                    OnlineSecurity,
                    OnlineBackup,
                    DeviceProtection,
                    TechSupport,
                    StreamingTV,
                    StreamingMovies,
                ],
            )

            predict_btn.click(
                predict_single,
                inputs=[
                    gender, SeniorCitizen, Partner, Dependents,
                    PhoneService, MultipleLines,
                    InternetService, OnlineSecurity, OnlineBackup,
                    DeviceProtection, TechSupport, StreamingTV, StreamingMovies,
                    tenure, Contract, PaperlessBilling, PaymentMethod,
                    MonthlyCharges, TotalCharges
                ],
                outputs=[risk, prob, segment, loss, cost, decision, action, explanation]
            )

        # ==================================================
        # BATCH CSV
        # ==================================================
        with gr.Tab("Batch CSV"):

            csv_file = gr.File(label="Upload CSV")
            batch_btn = gr.Button("Run Batch Prediction")
            batch_out = gr.File(label="Download Results")

            batch_btn.click(batch_predict, csv_file, batch_out)

demo.launch()
