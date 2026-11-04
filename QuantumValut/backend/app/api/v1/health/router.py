from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def health_check():
    return {
        "success": True,
        "message": "ClaudeVault API is healthy"
    }
