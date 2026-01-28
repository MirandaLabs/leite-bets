from fastapi import APIRouter
from scrapers.workflows.run_bet365 import run as run_bet365
from scrapers.workflows.run_betano import run as run_betano
from scrapers.base.betano.collector import collect as collect_betano_raw
from playwright.sync_api import sync_playwright

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/debug/betano-html")
def debug_betano_html():
    """Debug endpoint to check what HTML is being retrieved from Betano."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
        context = browser.new_context(
            locale="pt-BR",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        page.goto("https://www.betano.bet.br/sport/futebol/brasil/brasileirao-serie-a-betano/10016/?bt=matchresult", 
                  timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        html = page.content()
        browser.close()
        
        # Check for various selectors
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        
        # Save HTML to file for inspection
        import os
        os.makedirs("storage/debug", exist_ok=True)
        with open("storage/debug/betano.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        return {
            "html_length": len(html),
            "html_saved_to": "storage/debug/betano.html",
            "contains_data_qa": "data-qa=" in html,
            "event_elements": len(soup.select("div[data-qa='event']")),
            "event_selection_elements": len(soup.select("div[data-qa='event-selection']")),
            "spans_with_s_name": len(soup.select("span.s-name")),
            "event_title_spans": len(soup.select("span.event__title")),
            "sample_data_qa_values": [div.get("data-qa") for div in soup.select("div[data-qa]")][:20],
        }


@router.post("/scrape/bet365")
def scrape_bet365():
    data = run_bet365()
    return {
        "source": "bet365",
        "items": len(data),
        "data": data
    }


@router.post("/scrape/betano")
def scrape_betano():
    data = run_betano()
    return {
        "source": "betano",
        "items": len(data),
        "data": data
    }
