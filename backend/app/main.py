import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.analyze import router as analyze_router

load_dotenv()

app = FastAPI(
    title="Financial Risk & Investment Copilot API",
    version="0.1.0",
    description="Agentic AI investment decision-support platform for educational research use.",
)

origin = os.getenv("FRONTEND_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if origin == "*" else [origin],
    allow_credentials=False if origin == "*" else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Financial Risk & Investment Copilot API"}

app.include_router(analyze_router, prefix="/api")
