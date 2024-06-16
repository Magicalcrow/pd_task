from fastapi import FastAPI
from app.config.db_config import Base, engine
from app.routers import github_router
import os
from app.scheduler import start_scheduler
import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(github_router.router, prefix="/api")

@app.on_event("startup")
def on_startup():
	PIPEDRIVE_API_TOKEN = os.getenv("PIPEDRIVE_API_TOKEN")
	if PIPEDRIVE_API_TOKEN:
		start_scheduler(PIPEDRIVE_API_TOKEN)
	else:
		logging.error("Environment variable PIPEDRIVE_API_TOKEN must be set.")

