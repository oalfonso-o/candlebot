import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from candlebot.settings import Settings
from candlebot.api import strategies
from candlebot.api import backfill
from candlebot.api import forms

logging.basicConfig(
    level=logging.INFO,
    format=(
        '%(asctime)s %(name)16.16s %(funcName)10.10s %(levelname)7s: '
        '%(message)s'
    ),
    force=True,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.API_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(strategies.router)
app.include_router(backfill.router)
app.include_router(forms.router)


@app.get("/")
async def root():
    return {"message": "Hello Cryptopeople!"}
