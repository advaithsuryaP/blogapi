from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello World!"}

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