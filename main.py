import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.scraper import extract_domain_data
from core.llm_engine import generate_cold_email
from core.db import init_db, is_lead_processed, log_lead
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Edge eXtractor Webhook API")

@app.on_event("startup")
def startup_event():
    init_db()

class ScrapeRequest(BaseModel):
    url: str

@app.post("/scrape")
async def process_target(request: ScrapeRequest):
    # Normalize domain for database tracking
    domain = request.url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    
    if is_lead_processed(domain):
        return {"status": "skipped", "reason": "Lead already exists in database", "domain": domain}
    
    scraped_data = await extract_domain_data(request.url)
    if not scraped_data.get("vulnerabilities"):
        return {"status": "skipped", "reason": "No technical vulnerabilities found", "domain": domain}
    
    email_payload = generate_cold_email(domain, scraped_data["vulnerabilities"])
    
    log_lead(domain, scraped_data)
    
    # n8n ingests this response and routes it to the Gmail API node
    return {
        "status": "success",
        "domain": domain,
        "vulnerabilities": scraped_data["vulnerabilities"],
        "email_payload": email_payload
    }

