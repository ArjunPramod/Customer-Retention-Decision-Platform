import streamlit as st
import requests
import os

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

tabs = st.tabs(["Single Customer"])

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

    p = st.session_state.prediction

    with right:

        with st.container(border=True):
            st.markdown("### 📈 Risk Summary")
            st.text_input("Churn Risk", value=p.get("risk_level", ""), disabled=True)
            st.number_input("Churn Probability", value=float(p.get("churn_probability", 0)), disabled=True)

        with st.container(border=True):
            st.markdown("### 👤 Customer Segment")
            st.text_area(
                "Customer Segment",
                value=p.get("segment", ""),
                disabled=True,
                label_visibility="collapsed"
            )

        with st.container(border=True):
            st.markdown("### 💰 Economic Impact")
            c1, c2 = st.columns(2)
            with c1:
                st.number_input("Expected Loss ($)", value=float(p.get("expected_loss", 0)), disabled=True)
            with c2:
                st.number_input("Retention Cost ($)", value=float(p.get("retention_cost", 0)), disabled=True)

        with st.container(border=True):
            st.markdown("### 🎯 Retention Decision")
            st.text_input("Final Decision", value=p.get("decision", ""), disabled=True)
            st.text_area("Recommended Action", value=p.get("retention_action", ""), disabled=True)

        with st.container(border=True):
            st.markdown("### 🧠 Why This Decision?")
            st.text_area(
                "Explanation",
                value=p.get("explanation", ""),
                height=100,
                disabled=True,
                label_visibility="collapsed"
            )
