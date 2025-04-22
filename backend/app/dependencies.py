# backend/app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, SessionLocal
from app.core.security import decode_access_token
from app.db.crud import get_user_by_email

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)  # No extra params here
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if not payload or "sub" not in payload:
            raise credentials_exception
            
        user = await get_user_by_email(db, email=payload["sub"])
        if not user:
            raise credentials_exception
            
        return user
    except Exception as e:
        raise credentials_exception from e