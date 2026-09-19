from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(
    title="EcoRAG Backend",
    description="AI-powered biodiversity and environmental recommendation API",
    version="1.0.0"
)

app.include_router(
    router,
    prefix="/api"
)


@app.get("/")
def root():
    return {
        "message": "EcoRAG Backend is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
