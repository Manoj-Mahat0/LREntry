from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routes import router as api_router
from fastapi.staticfiles import StaticFiles
import os


# Create tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI()

# CORS Middleware for React frontend support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify frontend domain like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes from routes.py
app.include_router(api_router)


# ✅ Serve React Frontend Build
if os.path.exists("web"):
    app.mount("/", StaticFiles(directory="web", html=True), name="frontend")

@app.get("/")
async def root():
    return {"message": "LR Entry"}