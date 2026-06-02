# 🚀 Automated Content Pipeline

An end-to-end autonomous content generation system that reads topics from **Google Sheets**, generates articles using **Groq LLM (Llama 3.3 70B)**, scores content quality with AI, saves output as **Google Docs**, and orchestrates everything with **n8n** — all containerized with **Docker**.

---

## 📸 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        n8n Scheduler                        │
│              (triggers pipeline on a schedule)              │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP POST /run
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     Python Worker (Flask)                    │
│                                                             │
│  1. Auto-reset error rows → pending                         │
│  2. Fetch pending topics from Google Sheets                 │
│  3. Auto-generate topics if none pending                    │
│  4. Generate 200-word article via Groq LLM                  │
│  5. Score content (clarity, engagement, accuracy)           │
│  6. Save article as Google Doc to Drive                     │
│  7. Update Sheet with status + quality score                │
└──────┬──────────────────┬──────────────────┬───────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
 Google Sheets       Google Drive        Google Docs
 (topics/status)    (file storage)     (articles saved)

                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Streamlit Dashboard                         │
│         (metrics, topic table, document links, logs)        │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

- **Fully autonomous** — auto-generates topics when Sheet is empty, no manual input needed
- **AI content generation** — Groq Llama 3.3 70B writes 200-word articles per topic
- **AI quality scoring** — second LLM call scores each article on clarity, engagement, and accuracy
- **Google Docs output** — articles saved as formatted Google Docs in Drive
- **Auto-retry on failure** — error rows automatically reset to pending on next run
- **n8n orchestration** — visual workflow with schedule trigger, success logging, and email alerts
- **Streamlit dashboard** — real-time view of metrics, topics, document links, and pipeline logs
- **Dockerized** — all three services run with a single `docker compose up`
- **Exponential backoff** — retry logic via `tenacity` for all LLM and API calls
- **OAuth 2.0** — secure Google authentication via `google-auth-oauthlib`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq API (Llama 3.3 70B) |
| Orchestration | n8n |
| Backend | Python 3.11, Flask |
| Dashboard | Streamlit |
| Google Integration | Google Sheets, Drive, Docs APIs |
| Auth | OAuth 2.0 |
| Retry Logic | Tenacity (exponential backoff) |
| Containerization | Docker, Docker Compose |

---

## 📁 Project Structure

```
automated-content-pipeline/
├── docker-compose.yml          # Spins up n8n, python-worker, dashboard
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not committed)
├── pipeline/
│   ├── __init__.py
│   ├── llm.py                  # Groq content generation + quality scoring
│   ├── sheets.py               # Google Sheets read/write operations
│   ├── drive.py                # Google Drive/Docs file creation
│   ├── main.py                 # Core pipeline orchestration logic
│   └── server.py               # Flask webhook server for n8n
├── dashboard/
│   ├── __init__.py
│   └── app.py                  # Streamlit dashboard
└── credentials/                # Google OAuth credentials (not committed)
    ├── oauth_credentials.json
    └── token.json
```

---

## ⚙️ Setup

### Prerequisites
- Python 3.11+
- Docker Desktop
- Google Cloud account
- Groq API account

### 1. Clone the repo
```bash
git clone https://github.com/bjorn-cpu/automated-content-pipeline.git
cd automated-content-pipeline
```

### 2. Google Cloud Setup
1. Create a new project at https://console.cloud.google.com
2. Enable these APIs:
   - Google Sheets API
   - Google Drive API
   - Google Docs API
3. Go to **Credentials → Create OAuth 2.0 Client ID** (Desktop App)
4. Download the JSON and save as `credentials/oauth_credentials.json`
5. Add your Gmail to **OAuth consent screen → Test users**

### 3. Environment variables
Create a `.env` file in the root:
```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_CREDENTIALS_PATH=credentials/oauth_credentials.json
GOOGLE_TOKEN_PATH=credentials/token.json
SPREADSHEET_ID=your_google_sheet_id
DRIVE_FOLDER_ID=your_google_drive_folder_id
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=yourpassword
```

### 4. Google Sheets Structure
Create a sheet with two tabs:

**Sheet1** (topic queue):
| Topic | Status | Notes | Quality Score |
|---|---|---|---|
| AI in healthcare | pending | | |

**Logs** (pipeline logs):
| Timestamp | Status | Message |
|---|---|---|

### 5. Generate OAuth token
```bash
pip install -r requirements.txt
python -m pipeline.main
```
A browser will open — log in with Google and allow permissions. This creates `credentials/token.json`.

### 6. Run everything
```bash
docker compose up --build
```

| Service | URL |
|---|---|
| n8n workflow editor | http://localhost:5678 |
| Streamlit dashboard | http://localhost:8501 |
| Python worker API | http://localhost:5000 |

### 7. n8n Workflow Setup
1. Open http://localhost:5678
2. Create a new workflow
3. Add **Schedule Trigger** → set your desired interval
4. Add **HTTP Request** node → `POST http://python-worker:5000/run`
5. Add **IF** node → condition: `{{ $json.status }}` equals `success`
6. Success branch → **Google Sheets** node → append row to Logs tab
7. Error branch → **Gmail** node → send failure alert
8. Save → toggle **Active**

---

## 🔄 How It Works

1. n8n fires on schedule and sends a POST request to the Python worker
2. Worker auto-resets any `error` rows back to `pending`
3. If no pending topics exist, 3 topics are auto-generated and added to Sheet1
4. For each pending topic:
   - Groq generates a 200-word article
   - A second Groq call scores it on clarity, engagement, and accuracy
   - Article is saved as a Google Doc in your Drive folder
   - Sheet1 row is updated with `done: <doc_url>` and quality scores
5. n8n logs the run to the Logs tab
6. On any failure, Gmail sends an alert email

---

## 📊 Dashboard

Visit **http://localhost:8501** to see:
- Total / Done / Pending / Error counts
- Full topic table with statuses and quality scores
- Clickable links to every generated Google Doc
- Pipeline run logs with timestamps

---

## 🔑 Getting API Keys

- **Groq API key** — https://console.groq.com
- **Google OAuth credentials** — https://console.cloud.google.com
- **Spreadsheet ID** — from your Google Sheet URL: `.../spreadsheets/d/THIS_PART/edit`
- **Drive Folder ID** — from your Drive folder URL: `.../folders/THIS_PART`

---

## 📄 License

MIT
