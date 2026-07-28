from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager

from database import Base, engine

from routes import posts, users

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

app.include_router(posts.router, prefix = "/api/posts", tags = ["posts"])
app.include_router(users.router, prefix = "/api/users", tags = ["users"])

@app.get("/", include_in_schema = False)
def home():
    return "Hello World!"


