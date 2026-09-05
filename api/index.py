from fastapi import FastAPI

app = FastAPI()

@app.get("/api")
def home():
    return {
        "status": "ok",
        "service": "finvision-ai",
        "version": "v1"
    }

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "finvision-ai",
        "version": "v1"
    }