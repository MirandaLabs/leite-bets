from fastapi import FastAPI

from workflows.run_bet365 import run as run_bet365
from workflows.run_betano import run as run_betano

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scrape/bet365")
def scrape_bet365():
    return run_bet365()
