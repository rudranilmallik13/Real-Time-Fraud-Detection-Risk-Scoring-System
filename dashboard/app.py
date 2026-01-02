import os
import psycopg2
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Fraud Dashboard", layout="wide")
st.title("🚨 Real-Time Fraud Detection Dashboard")

# Read DB config from env (same as API)
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "fraud_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

try:
    conn = get_connection()

    query = """
    SELECT
        amount,
        hour,
        fraud_probability,
        risk_score,
        decision,
        top_reason,
        created_at
    FROM fraud_logs
    ORDER BY created_at DESC
    LIMIT 50;
    """

    df = pd.read_sql(query, conn)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", len(df))
    col2.metric("Blocked", (df["decision"] == "BLOCK").sum())
    col3.metric("Allowed", (df["decision"] == "ALLOW").sum())

    st.subheader("📋 Latest Transactions")
    st.dataframe(df, use_container_width=True)

    st.subheader("📊 Risk Score Distribution")
    st.bar_chart(df["risk_score"])

except Exception as e:
    st.error("❌ Database connection failed")
    st.code(str(e))
