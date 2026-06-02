import os
from googleapiclient.discovery import build
from pipeline.sheets import get_credentials
from dotenv import load_dotenv

load_dotenv()

def save_to_drive(filename: str, content: str) -> str:
    """Create a Google Doc in Drive folder and return the file URL."""
    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # Create empty Google Doc
    doc = docs_service.documents().create(
        body={"title": filename}
    ).execute()
    doc_id = doc["documentId"]

    # Insert content into the doc
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": content
                    }
                }
            ]
        }
    ).execute()

    # Move doc to your Drive folder
    folder_id = os.getenv("DRIVE_FOLDER_ID")
    drive_service.files().update(
        fileId=doc_id,
        addParents=folder_id,
        removeParents="root",
        fields="id, parents"
    ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"