from fastapi import FastAPI
from scrapers.api.routes import router

app = FastAPI()
app.include_router(router)
