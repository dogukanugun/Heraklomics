from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_analysis():
    return {"message": "✅ Analysis API is working"}
