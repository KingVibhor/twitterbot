from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./twitter_bot.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Twitter API setup
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
def read_root():
    # Serve the frontend HTML file
    from fastapi.responses import FileResponse
    return FileResponse("index.html")

@app.get("/app.js")
def get_app_js():
    from fastapi.responses import FileResponse
    return FileResponse("app.js")


@app.get("/api/stats")
def get_stats():
    return {
        "total_tweets": 150,
        "followers": 1250,
        "engagement_rate": 4.5,
        "last_tweet": "2024-01-15T10:30:00Z",
        "status": "active"
    }


@app.post("/api/add-quote")
def add_quote(quote: dict):
    # In a real implementation, you'd save this to your database
    return {
        "success": True,
        "message": "Quote added successfully",
        "quote_id": 123,
        "quote": quote
    }


@app.post("/api/settings")
def update_settings(settings: dict):
    # In a real implementation, you'd save these settings to your database
    return {
        "success": True,
        "message": "Settings updated successfully",
        "settings": settings
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
