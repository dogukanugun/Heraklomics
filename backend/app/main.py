from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import users, files
from app.core.config import settings

app = FastAPI(
    title="Heraclomics API",
    version="0.1.0",
    description="No-Code AI Bioinformatics Platform"
)

# Enable CORS (adjust origins as needed for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])

@app.get("/")
async def root():
    return {"message": "🚀 Heraclomics is up and running!"}
