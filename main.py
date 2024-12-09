from contextlib import asynccontextmanager

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import database
from routes import auth, session, venue


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield

    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(router=auth.router)
app.include_router(router=venue.router)
app.include_router(router=session.router)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/")
async def index():
    return {
        "app": "Student Engagement Api",
        "version": "0.0.1",
        "auther": "Gautam Makadia",
    }



if __name__ == "__main__":
    uvicorn.run(app= "main:app", host="0.0.0.0", port=8080, reload=True)