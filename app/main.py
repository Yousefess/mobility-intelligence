from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat

app = FastAPI(title="Mobility Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
