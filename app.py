import streamlit as st
import requests
import os
import shap
import numpy as np
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

st.set_page_config(page_title="Telecom Churn System", layout="wide")

# ------------------------------------------------
# Session State Init
# ------------------------------------------------

if "status" not in st.session_state:
    st.session_state.status = "⚪ Idle"

if "prediction" not in st.session_state:
    st.session_state.prediction = {}

# ------------------------------------------------
# Header
# ------------------------------------------------

h1, h2 = st.columns([4, 1])

with h1:
    st.markdown("""
    <h1 style="margin-bottom:0;">📊 Telecom Customer Retention Decision Platform</h1>
    <h4 style="margin-top:4px;color:#999;font-weight:400;">
    Predict churn risk, segment customers, and generate cost-aware retention actions
    </h4>
    """, unsafe_allow_html=True)

with h2:
    st.text_area(
        "System Status",
        value=st.session_state.status,
        height=40,
        disabled=True
    )

tabs = st.tabs(["Single Customer", "Batch Prediction", "Prediction History"])

# ==================================================
# SINGLE CUSTOMER
# ==================================================

with tabs[0]:

    left, right = st.columns(2)

    # ---------------- LEFT COLUMN ----------------

    with left:

        with st.expander("👤 Demographics", expanded=True):
            gender = st.selectbox("Gender", ["Female", "Male"], index=1)
            SeniorCitizen = st.radio("Senior Citizen", ["Yes", "No"], index=1, horizontal=True)
            Partner = st.radio("Partner", ["Yes", "No"], index=1, horizontal=True)
            Dependents = st.radio("Dependents", ["Yes", "No"], index=1, horizontal=True)

        with st.expander("📞 Phone Services"):
            PhoneService = st.radio("Phone Service", ["Yes", "No"], index=0, horizontal=True)

            if PhoneService == "No":
                MultipleLines = "No"
                st.selectbox("Multiple Lines", ["No"], disabled=True)
            else:
                MultipleLines = st.selectbox("Multiple Lines", ["Yes", "No"], index=1)

        with st.expander("🌐 Internet & Add-On Services"):
            InternetService = st.selectbox(
                "Internet Service",
                ["DSL", "Fiber optic", "No"],
                index=1
            )

            if InternetService == "No":
                opts = ["No"]
                disabled = True
                idx = 0
            else:
                opts = ["Yes", "No"]
                disabled = False
                idx = 1 

            OnlineSecurity = st.selectbox("Online Security", opts, index=idx, disabled=disabled)
            OnlineBackup = st.selectbox("Online Backup", opts, index=idx, disabled=disabled)
            DeviceProtection = st.selectbox("Device Protection", opts, index=idx, disabled=disabled)
            TechSupport = st.selectbox("Tech Support", opts, index=idx, disabled=disabled)
            StreamingTV = st.selectbox("Streaming TV", opts, index=idx, disabled=disabled)
            StreamingMovies = st.selectbox("Streaming Movies", opts, index=idx, disabled=disabled)

        with st.expander("🧾 Account Information"):
            tenure = st.number_input(
                "Tenure (months)", 
                min_value=1,
                max_value=72,
                value=None,
                placeholder="Enter tenure (1–72)"
            )
            Contract = st.selectbox(
                "Contract",
                ["Month-to-month", "One year", "Two year"],
                index=0
            )
            PaperlessBilling = st.radio("Paperless billing", ["Yes", "No"], index=0, horizontal=True)
            PaymentMethod = st.selectbox(
                "Payment Method",
                [
                    "Bank transfer (automatic)",
                    "Credit card (automatic)",
                    "Electronic check",
                    "Mailed check"
                ],
                index=2
            )

        with st.expander("💰 Financials"):
            MonthlyCharges = st.number_input(
                "Monthly Charges ($)", 
                min_value=18.0,
                max_value=120.0,
                value=None,
                placeholder="Enter monthly charges"
            )
            TotalCharges = st.number_input(
                "Total Charges ($)", 
                min_value=18.0, 
                max_value=8700.0,
                value=None,
                placeholder="Enter total charges"
            )
            if tenure is not None and MonthlyCharges is not None and TotalCharges is not None:
                expected = MonthlyCharges * tenure
                delta = abs(TotalCharges - expected)

                if expected > 0 and delta > 0.25 * expected:
                    st.warning("⚠ Total charges don’t match the monthly charge and tenure. Please double-check.")


        if st.button("Predict Customer"):
             
            missing = []

            if tenure is None:
                missing.append("Tenure")

            if MonthlyCharges is None:
                missing.append("Monthly Charges")

            if TotalCharges is None:
                missing.append("Total Charges")

            if missing:
                st.error(f"⚠ Please fill the following fields: {', '.join(missing)}")
            
            elif TotalCharges < MonthlyCharges:
                st.error("⚠ Total Charges cannot be less than Monthly Charges.")
            else:
                payload = {
                    "gender": gender,
                    "SeniorCitizen": SeniorCitizen,
                    "Partner": Partner,
                    "Dependents": Dependents,
                    "PhoneService": PhoneService,
                    "MultipleLines": MultipleLines,
                    "InternetService": InternetService,
                    "OnlineSecurity": OnlineSecurity,
                    "OnlineBackup": OnlineBackup,
                    "DeviceProtection": DeviceProtection,
                    "TechSupport": TechSupport,
                    "StreamingTV": StreamingTV,
                    "StreamingMovies": StreamingMovies,
                    "tenure": tenure,
                    "Contract": Contract,
                    "PaperlessBilling": PaperlessBilling,
                    "PaymentMethod": PaymentMethod,
                    "MonthlyCharges": MonthlyCharges,
                    "TotalCharges": TotalCharges,
                }

                try:
                    with st.spinner("Predicting..."):
                        r = requests.post(f"{FASTAPI_URL}/predict", json=payload, timeout=10)
                        r.raise_for_status()
                        st.session_state.prediction = r.json()
                        st.session_state.status = "🟢 Prediction successful"

                except requests.exceptions.ConnectionError:
                    st.session_state.prediction = {}
                    st.session_state.status = "🔴 Backend Offline"

                except requests.exceptions.Timeout:
                    st.session_state.prediction = {}
                    st.session_state.status = "🔴 Backend timed out."

                except requests.exceptions.HTTPError as e:
                    st.session_state.prediction = {}
                    st.session_state.status = f"🔴 HTTP error: {e}"

                except Exception as e:
                    st.session_state.prediction = {}
                    st.session_state.status = f"🔴 Unexpected error: {e}"

                st.rerun()

    # ---------------- RIGHT COLUMN ----------------

    with right:

        pred = st.session_state.prediction

        if pred:
            with st.container(border=True):

                st.subheader("📈 Churn Prediction Summary")

                # ---------- ROW 1 : Risk + Urgency ----------
                r1, r2 = st.columns(2)

                with r1:
                    st.metric(
                        "🔥 Churn Risk",
                        f"{pred['churn_probability']*100:.1f}%"
                    )

                with r2:
                    urgency = pred["urgency"].upper()

                    urgency_color = {
                        "HIGH": "🔴 HIGH",
                        "MEDIUM": "🟠 MEDIUM",
                        "LOW": "🟡 LOW",
                        "VERY_LOW": "🟢 VERY LOW"
                    }.get(urgency, urgency)

                    st.metric("⚡ Urgency", urgency_color)

                # ---------- ROW 2 : Persona ----------
                st.metric(
                    "👤 Persona",
                    pred["persona"]
                )

            with st.container(border=True):

                st.subheader("🧠 Why this customer may churn")

                for r in pred["top_reasons"]:
                    if r["value"]:
                        st.info(f"**{r['feature']} = {r['value']}**  \nImpact: {r['impact']:+.3f}")
                    else:
                        st.info(f"**{r['feature']}**  \nImpact: {r['impact']:+.3f}")
            
            with st.container(border=True):

                st.subheader("🎯 Recommended Retention Actions")

                for a in pred["recommended_actions"]:
                    st.checkbox(a, value=True)

            # ---------------- SHAP ----------------
            with st.container(border=True):

                with st.expander("📊 Explain Prediction (SHAP)", expanded=False):

                    shap_values = np.array(pred["shap_values"])
                    shap_base = pred["shap_base"]
                    shap_data = np.array(pred["shap_data"])
                    shap_features = pred["shap_features"]

                    shap_exp = shap.Explanation(
                        values=shap_values,
                        base_values=shap_base,
                        data=shap_data,
                        feature_names=shap_features
                    )

                    fig = plt.figure()
                    shap.plots.waterfall(shap_exp, show=False)
                    st.pyplot(fig, clear_figure=True)

        else:
            with st.container(border=True):
                st.info("Waiting for prediction…")

# ==================================================
# BATCH PREDICTION
# ==================================================

with tabs[1]:

    st.subheader("📂 Batch Customer Prediction")

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        help="Upload customer CSV with same schema as single prediction"
    )

    if uploaded_file is not None:

        try:
            input_df = pd.read_csv(uploaded_file)

            st.markdown("### 👀 Input CSV Preview")
            st.dataframe(input_df.head(20), use_container_width=True)

            if st.button("Run Batch Prediction", key="run_batch"):

                with st.spinner("Running batch inference..."):

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "text/csv"
                        )
                    }

                    response = requests.post(
                        f"{FASTAPI_URL}/predict_batch",
                        files=files,
                        timeout=60
                    )

                    response.raise_for_status()

                    results = response.json()
                    results_df = pd.DataFrame(results)

                    st.session_state["batch_results"] = results_df
                    st.session_state.status = "🟢 Batch prediction successful"

        except Exception as e:
            st.error(f"Batch failed: {e}")
            st.session_state.status = "🔴 Batch error"

    # ---------- Show Results ----------
    if "batch_results" in st.session_state:

        results_df = st.session_state["batch_results"]

        st.markdown("### 📊 Prediction Results Preview")
        st.caption(f"Rows scored: {len(results_df)}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("High Urgency", (results_df["urgency"] == "high").sum())

        with col2:
            st.metric("Medium Urgency", (results_df["urgency"] == "medium").sum())

        with col3:
            st.metric("Low / Very Low", (results_df["urgency"].isin(["low","very_low"])).sum())
        st.dataframe(results_df.head(50), use_container_width=True)

        # Download button
        csv_buffer = BytesIO()
        results_df.to_csv(csv_buffer, index=False)

        st.download_button(
            label="⬇️ Download Results CSV",
            data=csv_buffer.getvalue(),
            file_name="churn_batch_results.csv",
            mime="text/csv"
        )

# ==================================================
# PREDICTION HISTORY
# ==================================================

with tabs[2]:

    st.subheader("📜 Prediction History")

    # --------------------------------------------
    # Load data from FastAPI
    # --------------------------------------------

    try:
        response = requests.get(f"{FASTAPI_URL}/history", timeout=10)
        response.raise_for_status()

        history_df = pd.DataFrame(response.json())

        # Get total row count (separate lightweight call)
        count_resp = requests.get(f"{FASTAPI_URL}/history_count", timeout=10)
        total_rows = count_resp.json()["total"]

    except Exception as e:
        st.error(f"Failed to load history: {e}")
        history_df = pd.DataFrame()

    if history_df.empty:
        st.info("No prediction history found.")
        st.stop()

    # Ensure datetime conversion
    history_df["created_at"] = pd.to_datetime(history_df["created_at"])

    # ==================================================
    # SECTION 1 — KPIs
    # ==================================================
    with st.container(border=True):
    
        st.markdown("### 📊 Overview")

        st.caption(
            f"Showing latest {len(history_df)} of {total_rows} predictions"
        )

        total_predictions = len(history_df)
        high_urgency_count = (history_df["urgency"] == "high").sum()

        today = pd.Timestamp.utcnow().date()
        today_df = history_df[history_df["created_at"].dt.date == today]
        avg_churn_today = (
            today_df["churn_probability"].mean()
            if not today_df.empty else 0
        )

        k1, k2, k3 = st.columns(3)

        with k1:
            st.metric("Total Predictions", total_predictions)

        with k2:
            st.metric("High Urgency Count", high_urgency_count)

        with k3:
            st.metric("Avg Churn Today", f"{avg_churn_today:.3f}")

    # ==================================================
    # SECTION 2 — Filters
    # ==================================================
    with st.container(border=True):

        st.markdown("### 🔎 Filters")

        f1, f2, f3 = st.columns(3)

        with f1:
            urgency_filter = st.selectbox(
                "Urgency",
                ["All"] + sorted(history_df["urgency"].unique().tolist())
            )

        with f2:
            persona_filter = st.selectbox(
                "Persona",
                ["All"] + sorted(history_df["persona"].unique().tolist())
            )

        with f3:
            min_date = history_df["created_at"].min().date()
            max_date = history_df["created_at"].max().date()

            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

        # Apply filters
        filtered_df = history_df.copy()

        if urgency_filter != "All":
            filtered_df = filtered_df[
                filtered_df["urgency"] == urgency_filter
            ]

        if persona_filter != "All":
            filtered_df = filtered_df[
                filtered_df["persona"] == persona_filter
            ]

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df["created_at"].dt.date >= start_date) &
                (filtered_df["created_at"].dt.date <= end_date)
            ]

    # ==================================================
    # SECTION 3 — Table
    # ==================================================
    with st.container(border=True):

        st.markdown("### 📋 Recent Predictions")

        st.caption(f"Filtered rows: {len(filtered_df)}")

        st.dataframe(
            filtered_df[[
                "created_at",
                "churn_probability",
                "urgency",
                "persona",
                "cluster"
            ]].sort_values("created_at", ascending=False),
            use_container_width=True
        )