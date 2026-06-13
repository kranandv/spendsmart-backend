
from fastapi import FastAPI
from sqlalchemy import null

from models import Base
from database import engine
from routers import auth, expenses
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app= FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://spendsmart-frontend-5q27.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
Base.metadata.create_all(bind=engine)

# app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(auth.router)
app.include_router(expenses.router)

