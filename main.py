from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime
import os
from dotenv import load_dotenv
import tweepy
import openai
from apscheduler.schedulers.background import BackgroundScheduler

# ---------------------- ENV & App Setup ---------------------- #
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

# Static files
app.mount("/static", StaticFiles(directory="."), name="static")

# ---------------------- Database Setup ---------------------- #
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./twitter_bot.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    author = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class BotSetting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    hashtags = Column(String)
    post_time = Column(String)
    replies = Column(String)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------- Twitter & OpenAI ---------------------- #
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
)
twitter_api = tweepy.API(auth)
openai.api_key = OPENAI_API_KEY

# ---------------------- Routes ---------------------- #

@app.get("/")
def read_root():
    return {"status": "OK"}

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
def add_quote(quote: dict, db: Session = Depends(get_db)):
    text = f"{quote['content']} — {quote['author']}"
    try:
        # Save to DB
        new_quote = Quote(content=quote["content"], author=quote["author"])
        db.add(new_quote)
        db.commit()

        # Post to Twitter
        twitter_api.update_status(status=text)
        return {"success": True, "message": "Quote saved and tweeted"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/settings")
def update_settings(settings: dict, db: Session = Depends(get_db)):
    existing = db.query(BotSetting).first()
    if existing:
        existing.hashtags = ",".join(settings["hashtags"])
        existing.post_time = settings["postTime"]
        existing.replies = "\n".join(settings["replyMessages"])
    else:
        new_setting = BotSetting(
            hashtags=",".join(settings["hashtags"]),
            post_time=settings["postTime"],
            replies="\n".join(settings["replyMessages"])
        )
        db.add(new_setting)
    db.commit()
    return {
        "success": True,
        "message": "Settings saved",
        "settings": settings
    }

# ---------------------- Quote Generator (AI) ---------------------- #
def generate_quote():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": "Give me a short motivational quote."
        }]
    )
    return response['choices'][0]['message']['content']

# ---------------------- Scheduled Daily Tweet ---------------------- #
scheduler = BackgroundScheduler()

def scheduled_post():
    db = SessionLocal()
    try:
        latest = db.query(Quote).order_by(Quote.timestamp.desc()).first()
        if latest:
            status = f"{latest.content} — {latest.author}"
            twitter_api.update_status(status=status)
            print("✅ Tweet posted:", status)
        else:
            print("ℹ️ No quotes to tweet.")
    except Exception as e:
        print("❌ Scheduled tweet failed:", str(e))
    finally:
        db.close()

# Schedule the job at 9:00 AM every day
scheduler.add_job(scheduled_post, 'cron', hour=9, minute=0)
scheduler.start()

# ---------------------- App Start ---------------------- #
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=False)
