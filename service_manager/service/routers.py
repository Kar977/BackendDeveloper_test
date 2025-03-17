import time
from typing import List

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from service_manager.database_structure.database import get_db
from service_manager.database_structure.models import User, Post
from service_manager.database_structure.schemas import UserCreate, UserLogin, PostCreate, PostResponse, UserResponse
from service_manager.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter()

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"


def verify_token(token: str):
    """
    Verifies the JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")


@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user.
    """
    user_data = User(email=user.email, password_hash=user.password)
    db.add(user_data)
    await db.commit()
    await db.refresh(user_data)
    return user_data


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Log in an existing user, generating a JWT token.
    """
    stmt = select(User).filter(User.email == user.email)
    result = await db.execute(stmt)
    db_user = result.scalars().first()

    if not db_user or db_user.password_hash != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": db_user.email, "exp": time.time() + 3600}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/post", response_model=PostResponse)
async def add_post(post: PostCreate, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Add a new post. Requires authentication via token.
    """
    user_payload = verify_token(token)
    user_email = user_payload.get("sub")

    stmt = select(User).filter(User.email == user_email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    new_post = Post(text=post.text, user_id=user.id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


@router.get("/posts", response_model=List[PostResponse])
async def get_posts(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Get all posts for the current user. Uses in-memory caching.
    """
    user_payload = verify_token(token)
    user_email = user_payload.get("sub")

    stmt = select(User).filter(User.email == user_email).options(selectinload(User.posts))
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    cached_posts = user.posts
    return cached_posts


@router.delete("/post/{post_id}")
async def delete_post(post_id: int, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Delete a specific post by ID. Requires authentication via token.
    """
    user_payload = verify_token(token)
    user_email = user_payload.get("sub")

    stmt = select(Post).filter(Post.id == post_id).join(User).filter(User.email == user_email)
    result = await db.execute(stmt)
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found or you don't have permission")

    await db.delete(post)
    await db.commit()
    return {"detail": "Post deleted"}
