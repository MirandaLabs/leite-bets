from fastapi import FastAPI
from workflows.run_betano import run

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/scrape")
def scrape():
    data = run()
    return {
        "source": "betano",
        "items": len(data),
        "data": data
    }
