@app.get("/api/health")
def health_api():
    return {
        "status": "ok",
        "service": "finvision-ai",
        "version": "v1"
    }
