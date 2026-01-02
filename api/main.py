import os
import pickle
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import shap
import numpy as np
import logging
from alerts.email_alert import send_email_alert

# =============================
# FASTAPI APP
# =============================
app = FastAPI()
logger = logging.getLogger("fraud_api")
logger.setLevel(logging.INFO)

# Globals to be set on startup
model = None
explainer = None

# =============================
# MODEL PATH
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "fraud_model.pkl")

@app.on_event("startup")
def load_model_and_explainer():
    global model, explainer
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        # Try to create a SHAP explainer; be tolerant to model type
        try:
            explainer = shap.TreeExplainer(model)
        except Exception:
            try:
                explainer = shap.Explainer(model)
            except Exception as e:
                logger.warning("Failed to create SHAP explainer: %s", e)
                explainer = None
        logger.info("Model loaded from %s", MODEL_PATH)
    except Exception as e:
        logger.exception("Failed to load model: %s", e)
        model = None
        explainer = None

# =============================
# FEATURES
# =============================
FEATURES = [
    "amount",
    "hour",
    "location_risk",
    "device_risk",
    "previous_fraud_count"
]

# =============================
# INPUT SCHEMA
# =============================
class Transaction(BaseModel):
    amount: float
    hour: int
    location_risk: int
    device_risk: int
    previous_fraud_count: int

# =============================
# DB CONNECTION
# =============================
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5433")),
        database=os.getenv("DB_NAME", "fraud_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "postgres")
    )

# =============================
# HEALTH
# =============================
@app.get("/")
def health():
    return {"status": "API is running"}

# =============================
# PREDICT
# =============================
def _extract_shap_top_reason(df):
    if explainer is None:
        return "unavailable"
    try:
        # Support both old and new shap APIs
        vals = None
        try:
            vals = explainer.shap_values(df)
        except Exception:
            try:
                ev = explainer(df)
                vals = getattr(ev, "values", None) or getattr(ev, "values", None)
            except Exception:
                vals = None

        if vals is None:
            return "unavailable"

        if isinstance(vals, list):
            vals = vals[0]
        vals = np.array(vals)
        return FEATURES[np.abs(vals[0]).argmax()]
    except Exception as e:
        logger.warning("SHAP extraction failed: %s", e)
        return "unavailable"

@app.post("/predict")
def predict(txn: Transaction):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    df = pd.DataFrame([txn.dict()])
    df = df[FEATURES].astype(float)

    # --- Prediction ---
    try:
        if hasattr(model, "predict_proba"):
            prob = float(model.predict_proba(df)[0][1])
        else:
            prob = float(model.predict(df)[0])
    except Exception as e:
        logger.exception("Prediction failed: %s", e)
        raise HTTPException(status_code=500, detail="Prediction error")

    risk = prob * 100
    decision = "BLOCK" if risk > 60 else "ALLOW"

    # --- SHAP ---
    top_reason = _extract_shap_top_reason(df)

    # --- DB LOGGING ---
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO fraud_logs
            (amount, hour, location_risk, device_risk, previous_fraud_count,
             fraud_probability, risk_score, decision, top_reason)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                txn.amount,
                txn.hour,
                txn.location_risk,
                txn.device_risk,
                txn.previous_fraud_count,
                prob,
                risk,
                decision,
                top_reason
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.exception("DB logging failed: %s", e)

    # --- ALERTING (✅ NOW EXECUTES) ---
    ALERT_THRESHOLD = 60  # testing

    if risk > ALERT_THRESHOLD:
        logger.info("🚨 ALERT TRIGGERED: risk=%s", risk)
        try:
            send_email_alert(txn.dict(), risk, top_reason)
        except Exception as e:
            logger.exception("Alert sending failed: %s", e)



    # --- RESPONSE ---
    return {
        "fraud_probability": round(prob, 2),
        "risk_score": round(risk, 1),
        "decision": decision,
        "top_reason": top_reason
    }

