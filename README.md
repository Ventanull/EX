# Edge eXtractor – Quick Start Guide

## Overview
This repository implements the **Edge eXtractor** pipeline:
- **Docker‑compose** spins up a local **n8n** instance (port 5678) and a **FastAPI** API (port 8000).
- The API receives a URL from n8n, scrapes the site for technical vulnerabilities, logs the lead in SQLite, and generates a hyper‑personalised cold‑email via OpenAI (LangChain).

## Prerequisites
- **Docker Desktop** (or Docker Engine) installed and running on Windows. Ensure `docker` is available in PowerShell/Command Prompt.
- **PowerShell 5+** (default on Windows 10/11).
- An **OpenAI API key** (free‑tier works) and **Gmail OAuth credentials** for the burner account you’ll use.

## 1️⃣ Setup the project
```powershell
# Clone / navigate to the project directory
cd d:\codes\projects\EX\n8n-arbitrage-engine
```

### Environment variables
Copy the example and fill in your real credentials:
```powershell
cp .env.example .env   # or manually duplicate the file
# Edit .env with a text editor (e.g., notepad) and replace the placeholders:
# OPENAI_API_KEY=sk-...
# GMAIL_CLIENT_ID=...
# GMAIL_CLIENT_SECRET=...
# DB_PATH=./data/leads.db
```

## 2️⃣ Build & start the containers
```powershell
# Build images and start containers in detached mode
docker compose up --build -d
```
Docker will pull the Python base image, install the Python packages from `requirements.txt`, and launch:
- **n8n** – UI at `http://localhost:5678`
- **FastAPI** – API at `http://localhost:8000`

## 3️⃣ Verify the FastAPI webhook
```powershell
$body = @{ url = "https://example.com" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/scrape" -Method Post -Body $body -ContentType "application/json"
```
You should see a JSON response similar to:
```json
{
  "status": "success",
  "domain": "example.com",
  "vulnerabilities": ["Missing or misconfigured SSL certificate", "Missing Facebook/Meta tracking pixel (potential ad‑spend waste)"],
  "email_payload": {
    "subject": "Quick audit to fix SSL & tracking issues",
    "body": "..."
  }
}
```
If the domain has no issues or is already in the DB, the response will be `"status": "skipped"`.

## 4️⃣ Wire n8n to the API
1. Open the n8n UI: <http://localhost:5678>.
2. Create a **New Workflow**.
3. Add an **HTTP Request** node:
   - **Method:** `POST`
   - **URL:** `http://host.docker.internal:8000/scrape`
   - **Body (JSON):** `{"url": "={{ $json.website }}"}`
4. Add a **Gmail** node (install the Gmail credential via n8n’s credential manager) and map `email_payload`:
   - **Subject:** `{{$json.email_payload.subject}}`
   - **Body:** `{{$json.email_payload.body}}`
5. Connect the nodes, activate the workflow, and test it with a sample input record.

## 5️⃣ Next development steps
- **Step 3 – Upgrade Scraper**: Replace the simple `httpx/BeautifulSoup` scraper with a Playwright‑based headless browser for richer data (e.g., screenshots, JS‑rendered content).
- **Step 4 – Tune LangChain**: Refine the prompt, experiment with other LLM models (e.g., Claude, Gemini) or a local LLM.
- **Add tests**: Unit tests for `core/*` modules using `pytest`.
- **Persist extra lead data**: Expand the SQLite schema (status, email sent timestamp, etc.).

---
*If you hit any Docker build errors or the API test fails, paste the full error output here and I’ll help you troubleshoot.*

