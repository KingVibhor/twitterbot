from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import tweepy
import os
import google.generativeai as genai

# ---------------------- ENV & App Setup ---------------------- #
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ---------------------- Twitter & Gemini ---------------------- #
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
)
twitter_api = tweepy.API(auth)
genai.configure(api_key=GEMINI_API_KEY)

# ---------------------- Routes ---------------------- #
@app.api_route("/", methods=["GET", "HEAD"])
def read_root(request: Request):
    return FileResponse("index.html")

@app.get("/app.js")
def get_app_js():
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
        new_quote = Quote(content=quote["content"], author=quote["author"])
        db.add(new_quote)
        db.commit()
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

@app.get("/api/latest-tweet")
def latest_tweet(db: Session = Depends(get_db)):
    latest = db.query(Quote).order_by(Quote.timestamp.desc()).first()
    if latest:
        return {
            "text": f"{latest.content} — {latest.author}",
            "time": latest.timestamp.isoformat()
        }
    return JSONResponse(status_code=404, content={"message": "No tweet found."})

@app.get("/api/scheduler-status")
def scheduler_status(db: Session = Depends(get_db)):
    today = date.today()
    latest = db.query(Quote).order_by(Quote.timestamp.desc()).first()
    if latest and latest.timestamp.date() == today:
        return {
            "tweeted_today": True,
            "time": latest.timestamp.isoformat()
        }
    else:
        return {
            "tweeted_today": False,
            "time": None
        }

# ---------------------- Scheduled Daily Tweet ---------------------- #
scheduler = BackgroundScheduler()

def generate_quote_with_gemini():
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content("Give me a short motivational quote with the author's name.")
        quote = response.text.strip()

        if "—" in quote:
            content, author = map(str.strip, quote.split("—", 1))
        elif "-" in quote:
            content, author = map(str.strip, quote.split("-", 1))
        else:
            content, author = quote, "Anonymous"

        return content, author
    except Exception as e:
        print("⚠️ Gemini generation failed:", str(e))
        return "Stay positive!", "Anonymous"

def scheduled_post():
    db = SessionLocal()
    try:
        print("📢 Running scheduled_post at", datetime.utcnow().isoformat())
        content, author = generate_quote_with_gemini()
        status = f"{content} — {author}"

        new_quote = Quote(content=content, author=author)
        db.add(new_quote)
        db.commit()

        twitter_api.update_status(status=status)
        print("✅ Tweeted:", status)

    except Exception as e:
        print("❌ Error during tweet:", str(e))
    finally:
        db.close()

try:
    scheduler.add_job(scheduled_post, 'cron', hour=8, minute=5)
    scheduler.add_job(
        scheduled_post,
        'date',
        run_date=datetime.utcnow() + timedelta(minutes=2),
        id="initial_tweet"
    )
    scheduler.start()
except Exception as e:
    print("❌ Scheduler failed to start:", str(e))

# ---------------------- App Start ---------------------- #
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=False)
