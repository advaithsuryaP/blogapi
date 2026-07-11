from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Advaith",
        "content": "This is a test post",
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01"
    },
    {
        "id": 2,
        "author": "John Doe",
        "content": "This is a test post 2",
        "created_at": "2026-01-02",
        "updated_at": "2026-01-02"
    }        
]


@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "Home"})

@app.get("/api/posts")
def get_posts():
    return posts

@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")