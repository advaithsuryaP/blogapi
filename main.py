from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from schemas import PostCreate, PostResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 1,
        "title": "First Post",
        "author": "Advaith",
        "content": "This is a test post",
        "date_posted": "Aptil 2nd 2026"
    },
    {
        "id": 2,
        "title": "Second Post",
        "author": "John Doe",
        "content": "This is a test post 2",
        "date_posted": "May 3nd 2026"
    }        
]


@app.get("/", include_in_schema = False)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "Home"})

@app.get("/api/posts", response_model = list[PostResponse])
def get_posts():
    return posts

@app.get("/api/posts/{post_id}", response_model = PostResponse)
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post("/api/posts", response_model = PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    new_id = max(p["id"] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "July 18th 2026"
    }
    posts.append(new_post)
    return new_post

