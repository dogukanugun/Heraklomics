from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User, UploadRecord
from app.schemas.user import UserCreate
from app.core.security import hash_password
from sqlalchemy import update
from sqlalchemy.orm import Session
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_pw = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def create_upload_record(db: AsyncSession, *, user_id: int, analysis_type: str, filename: str, saved_path: str):
    record = UploadRecord(
        user_id=user_id,
        analysis_type=analysis_type,
        original_filename=filename,
        saved_path=saved_path,
        status="uploaded"
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record

async def update_upload_status(
    db: AsyncSession,
    upload_id: int,
    status: str
):
    """
    Asynchronously update the status of an upload record.
    """
    await db.execute(
        update(UploadRecord)
          .where(UploadRecord.id == upload_id)
          .values(status=status)
    )
    await db.commit()

def update_upload_status_sync(
    db: Session,
    upload_id: int,
    status: str
):
    """
    Synchronously update the status of an upload record
    (for use in Celery tasks or other sync contexts).
    """
    db.execute(
        update(UploadRecord)
          .where(UploadRecord.id == upload_id)
          .values(status=status)
    )
    db.commit()