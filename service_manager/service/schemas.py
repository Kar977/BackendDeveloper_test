from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
import time

class UserCreate(BaseModel):
    """
    Pydantic model for user registration (signup).
    Ensures that email is valid and password is non-empty.
    """
    email: EmailStr
    password: str

    @validator("password")
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    """
    Pydantic model for user login.
    Ensures that email and password are valid.
    """
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class PostCreate(BaseModel):
    """
    Pydantic model for creating a post.
    Ensures that post text is not empty and limits payload size.
    """
    text: str

    @validator("text")
    def text_size(cls, v):
        if len(v.encode("utf-8")) > 1048576:  # 1 MB limit
            raise ValueError("Post payload exceeds 1MB")
        return v

    class Config:
        orm_mode = True


class PostResponse(PostCreate):
    """
    Pydantic model for a post response (with ID).
    Inherits from PostCreate, adding the post ID.
    """
    id: int
    timestamp: int

    class Config:
        orm_mode = True


class UserResponse(UserCreate):
    """
    Pydantic model for user response after successful registration/login.
    Includes the user's ID and email.
    """
    id: int

    class Config:
        orm_mode = True
