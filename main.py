from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return """
    <html>
        <head>
            <title>My Website</title>
        </head>
        <body>
            <h1>Hello World!</h1>
        </body>
    </html>
    """

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