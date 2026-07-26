from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_404_NOT_FOUND

from schemas import PostCreate, PostResponse, UserCreate, UserResponse, PostUpdate

from sqlalchemy import select
from sqlalchemy.orm import Session

from typing import Annotated

import models
from database import Base, engine, get_db

Base.metadata.create_all(bind = engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory = "static"), name = "static")
app.mount("/media", StaticFiles(directory = "media"), name = "media")

templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema = False)
def home():
    return "Hello World!"

@app.get("/api/posts", response_model = list[PostResponse])
def get_posts(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts

@app.get("/api/posts/{post_id}", response_model = PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id== post_id))
    post = result.scalars().first()

    if post:
        return post
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post not found")


@app.put("/api/posts/{post_id}", response_model = PostResponse)
def update_post(post_id: int, post_data: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id== post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post not found")

    if post_data.user_id != post.user_id:
        result = db.execute(select(models.user).where(models.User.id == post.user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code = HTTP_404_NOT_FOUND, detail = "User not found")

    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    db.commit()
    db.refresh(post)
    return post

@app.patch("/api/posts/{post_id}", response_model = PostResponse)
def patch_post(post_id: int, post_data: PostUpdate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id== post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post not found")

    update_data = post_data.model_dump(exclude_unset = True)
    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post

@app.post("/api/posts", response_model = PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code = HTTP_404_NOT_FOUND, detail = "User not found")

    new_post = models.Post(
        title = post.title,
        content = post.content,
        user_id = post.user_id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post        


@app.get("/api/users", response_model = list[UserResponse])
def get_posts(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User))
    users = result.scalars().all()
    return users

@app.post("/api/users", response_model = UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    username_result = db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = username_result.scalars().first()

    if existing_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail = "Username already exists")
    
    email_result = db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = email_result.scalars().first()

    if existing_email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail = "Email already exists")


    new_user = models.User(
        username = user.username,
        email = user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
    

@app.get("/api/users", response_model = list[UserResponse])
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id== user_id))
    user = result.scalars().first()

    if user:
        return user
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")

@app.get("/api/users/{user_id}/posts", response_model = list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id== user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code = HTTP_404_NOT_FOUND, detail = "User not found")
    
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts

