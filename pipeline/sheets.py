import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

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
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds

def get_pending_topics():
    """Fetch rows from Google Sheets where status is 'pending'."""
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A:D"
    ).execute()

    rows = result.get("values", [])
    pending = []

    for i, row in enumerate(rows[1:], start=2):
        if len(row) >= 2 and row[1].lower() == "pending":
            pending.append({"row": i, "topic": row[0]})

    return pending

def update_status(row_number: int, status: str):
    """Update the status column for a given row."""
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"Sheet1!B{row_number}",
        valueInputOption="RAW",
        body={"values": [[status]]}
    ).execute()

def update_score(row_number: int, scores: dict):
    """Write quality scores to column D."""
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    score_text = f"C:{scores.get('clarity',0)} E:{scores.get('engagement',0)} A:{scores.get('accuracy',0)} Overall:{scores.get('overall',0)}"
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"Sheet1!D{row_number}",
        valueInputOption="RAW",
        body={"values": [[score_text]]}
    ).execute()

def add_topic_to_sheet(topic: str):
    """Add an auto-generated topic to Sheet1 as pending."""
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A:D",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [[topic, "pending", "", ""]]}
    ).execute()

def reset_error_rows():
    """Reset all 'error' rows back to 'pending' for retry."""
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A:D"
    ).execute()

    rows = result.get("values", [])
    for i, row in enumerate(rows[1:], start=2):
        if len(row) >= 2 and row[1].lower() == "error":
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"Sheet1!B{i}",
                valueInputOption="RAW",
                body={"values": [["pending"]]}
            ).execute()
            print(f"Reset row {i} back to pending")