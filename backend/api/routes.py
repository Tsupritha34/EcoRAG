from fastapi import APIRouter
from backend.services.eco_service import EcoService


router = APIRouter()

eco_service = EcoService()


@router.get("/status")
def api_status():
    return {
        "message": "EcoRAG API is working",
        "status": "success"
    }


@router.post("/analyze")
def analyze_environment(data: dict):
    result = eco_service.analyze(data)

    return {
        "status": "success",
        "data": result
    }