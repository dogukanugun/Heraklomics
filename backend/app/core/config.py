from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Heraclomics"
    API_VERSION: str = "v1"
    SECRET_KEY: str = "1c4a193e126c20048a59175bd493c3d4e7c582f8432840788c2132b383ff5f04"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./heraclomics.db"

    class Config:
        case_sensitive = True

settings = Settings()
