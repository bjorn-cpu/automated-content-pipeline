import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents"
]

def get_credentials():
    creds = None
    token_path = os.getenv("GOOGLE_TOKEN_PATH")
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    return creds

def get_sheet_data():
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A:D"
    ).execute()

    rows = result.get("values", [])
    if len(rows) <= 1:
        return pd.DataFrame()

    headers = ["Topic", "Status", "Notes", "Quality Score"]
    data = []
    for row in rows[1:]:
        while len(row) < 4:
            row.append("")
        data.append(row)

    return pd.DataFrame(data, columns=headers)

def get_logs_data():
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Logs!A:C"
    ).execute()

    rows = result.get("values", [])
    if len(rows) <= 1:
        return pd.DataFrame()

    headers = ["Timestamp", "Status", "Message"]
    data = []
    for row in rows[1:]:
        while len(row) < 3:
            row.append("")
        data.append(row)

    return pd.DataFrame(data, columns=headers)

# --- UI ---
st.set_page_config(page_title="Content Pipeline Dashboard", layout="wide")
st.title("🚀 Automated Content Pipeline")
st.caption("Powered by Groq LLM + Google Sheets + Google Drive + n8n")

if st.button("🔄 Refresh Data"):
    st.rerun()

df = get_sheet_data()
logs = get_logs_data()

if df.empty:
    st.warning("No data found in Sheet1.")
else:
    # --- Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    total = len(df)
    done = len(df[df["Status"].str.startswith("done", na=False)])
    pending = len(df[df["Status"].str.lower() == "pending"])
    errors = len(df[df["Status"].str.lower() == "error"])

    col1.metric("Total Topics", total)
    col2.metric("✅ Done", done)
    col3.metric("⏳ Pending", pending)
    col4.metric("❌ Errors", errors)

    st.divider()

    # --- Topics Table ---
    st.subheader("📋 Topics")
    st.dataframe(df, use_container_width=True)

    # --- Drive Links ---
    st.subheader("📄 Generated Documents")
    done_rows = df[df["Status"].str.startswith("done", na=False)]
    if done_rows.empty:
        st.info("No documents generated yet.")
    else:
        for _, row in done_rows.iterrows():
            url = row["Status"].replace("done: ", "")
            score = row["Quality Score"] if row["Quality Score"] else "N/A"
            st.markdown(f"**{row['Topic']}** — Score: `{score}` — [Open Doc]({url})")

    st.divider()

    # --- Logs ---
    st.subheader("📊 Pipeline Logs")
    if logs.empty:
        st.info("No logs yet.")
    else:
        st.dataframe(logs, use_container_width=True)