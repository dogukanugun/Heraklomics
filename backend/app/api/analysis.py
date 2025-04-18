from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/test")
async def test_analysis():
    return {"message": "✅ Analysis API is working"}

class UploadRecordResponse(BaseModel):
    id: int
    analysis_type: str
    original_filename: str
    saved_path: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True