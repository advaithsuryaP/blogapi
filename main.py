from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from schemas import PostCreate, PostResponse, UserCreate, UserResponse, PostUpdate, UserUpdate

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from typing import Annotated
from contextlib import asynccontextmanager

from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

import models
from database import Base, engine, get_db

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shtdown
    await engine.dispose()

app = FastAPI(lifespan = lifespan)

app.mount("/static", StaticFiles(directory = "static"), name = "static")
app.mount("/media", StaticFiles(directory = "media"), name = "media")

templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema = False)
def home():
    return "Hello World!"

@app.post("/api/posts", response_model = PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code = HTTP_404_NOT_FOUND, detail = "User not found")

    new_post = models.Post(
        title = post.title,
        content = post.content,
        user_id = post.user_id
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names = ["author"])

    return new_post

@app.get("/api/posts", response_model = list[PostResponse])
async def get_posts(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)))
    posts = result.scalars().all()
    return posts

@app.get("/api/posts/{post_id}", response_model = PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()

    if post:
        return post
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post not found")


@app.put("/api/posts/{post_id}", response_model = PostResponse)
async def update_post(post_id: int, post_data: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post not found")

    if post_data.user_id != post.user_id:
        result = await db.execute(select(models.user).where(models.User.id == post.user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code = HTTP_404_NOT_FOUND, detail = "User not found")

    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    await db.commit()
    await db.refresh(post, attribute_names = ["author"])
    return post

@app.patch("/api/posts/{post_id}", response_model = PostResponse)
async def patch_post(post_id: int, post_data: PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post not found")

    update_data = post_data.model_dump(exclude_unset = True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post, attribute_names = ["author"])
    return post

@app.delete("/api/posts/{post_id}", status_code = HTTP_204_NO_CONTENT)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post not found")

    await db.delete(post)
    await db.commit()  


@app.post("/api/users", response_model = UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    username_result = await db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = username_result.scalars().first()

    if existing_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail = "Username already exists")
    
    email_result = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = email_result.scalars().first()

    if existing_email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail = "Email already exists")

    new_user = models.User(
        username = user.username,
        email = user.email,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@app.get("/api/users", response_model = list[UserResponse])
async def get_users(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return users


@app.get("/api/users/{user_id}", response_model = UserResponse)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if user:
        return user
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")

@app.patch("/api/users/{user_id}", response_model = UserResponse)
async def patch_user(user_id: int, user_data: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")

    if user_data.username is not None and user.username != user.username:
        username_result = await db.execute(select(models.User).where(models.User.username == user_data.username))
        existing_username = username_result.scalars().first()
        if existing_username:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Username already exists")
    
    if user_data.email is not None and user.email != user.email:
        email_result = await db.execute(select(models.User).where(models.User.email == user_data.email))
        existing_email = email_result.scalars().first()
        if existing_email:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Email already registered")

    if user_data.username is not None:
        user.username = user_data.username      
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.image_file is not None:
        user.image_file = user_data.image_file

    await db.commit()
    await db.refresh(user)
    return user


@app.delete("/api/users/{user_id}", status_code = HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    
    await db.delete(user)
    await db.commit()

@app.get("/api/users/{user_id}/posts", response_model = list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code = HTTP_404_NOT_FOUND, detail = "User not found")
    
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts

