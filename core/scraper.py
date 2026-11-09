import httpx
from bs4 import BeautifulSoup
import ssl
import socket
from urllib.parse import urlparse

async def extract_domain_data(url: str) -> dict:
    """Asynchronously scrape a given URL and detect technical vulnerabilities.
    Returns a dict with a ``vulnerabilities`` list. If the request fails, the list
    will contain a descriptive error message.
    """
    # Ensure we have a scheme for ``urlparse`` and socket connections
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    vulnerabilities = []

    # 1️⃣ SSL Handshake check – attempt a TLS connection on port 443
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=3) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain):
                pass  # successful handshake
    except Exception:
        vulnerabilities.append("Missing or misconfigured SSL certificate")

    # 2️⃣ HTTP GET and DOM analysis
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
        if response.status_code != 200:
            vulnerabilities.append(f"Server returned status code {response.status_code}")
            return {"vulnerabilities": vulnerabilities}

        html = response.text.lower()
        soup = BeautifulSoup(html, "lxml")

        # Meta Pixel / Facebook tracking
        if "fbevents.js" not in html and "fbq('init'" not in html:
            vulnerabilities.append("Missing Facebook/Meta tracking pixel (potential ad‑spend waste)")

        # Google Tag Manager
        if "gtm.js" not in html and "googletagmanager.com" not in html:
            vulnerabilities.append("Google Tag Manager not installed")

        # Basic SEO checks
        if not soup.title or not soup.title.string or not soup.title.string.strip():
            vulnerabilities.append("Missing <title> tag for SEO")
        if not soup.find("h1"):
            vulnerabilities.append("Landing page lacks a primary <h1> heading")
    except Exception as exc:
        vulnerabilities.append("Domain timed out or connection refused during scrape")

    return {"vulnerabilities": vulnerabilities}

