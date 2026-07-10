from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html")

@app.get("/api/posts")
def get_posts():
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
    return posts