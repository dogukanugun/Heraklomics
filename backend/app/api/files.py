from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_files():
    return {"message": "✅ Files API is working"}
