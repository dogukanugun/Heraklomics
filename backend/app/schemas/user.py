from pydantic import BaseModel, EmailStr

# Used when creating a new user (registration)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Used when logging in
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Used when returning user data in responses
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True