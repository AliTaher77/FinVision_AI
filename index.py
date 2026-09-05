from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FinVision AI", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "finvision-ai",
        "version": "v1"
    }

@app.get("/api/risk-summary")
def risk_summary():
    return {
        "asset": "USD/YER",
        "risk_level": "medium",
        "predicted_trend": "up",
        "sentiment": "neutral",
        "disclaimer": "Educational analysis only"
    }
