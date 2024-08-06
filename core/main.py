from fastapi import FastAPI
from . import models
from .database import engine
from .logging import setup_logging
from .routers import post, users, auth, vote
# from .config import settings

from fastapi.middleware.cors import CORSMiddleware
# *******************************************
# This is necessary once we are
# using alembic to handle database migrations
# models.Base.metadata.create_all(bind=engine)
# *******************************************

app = FastAPI()

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""/// Logging /////"""
setup_logging()
"""/// Logging /////"""

app.include_router(post.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(vote.router)

 
@app.get("/")
def root():
    return {"message": "Hello world"}
