# 🐦 AI-Powered Twitter Bot using FastAPI + Google Gemini

An automated motivational quote tweeting bot that generates fresh quotes daily using **Google Gemini** and posts them on **Twitter (X)** using **Tweepy**. Built with **FastAPI**, the project includes a web dashboard to view tweet history and bot stats.

---

## 🔥 Features

- 🧠 AI-generated motivational quotes using **Google Gemini**
- 🐦 Tweets daily at a scheduled time via **Twitter API (OAuth 1.0a)**
- 🗂 Stores all quotes in a database (SQLite/PostgreSQL)
- ⏰ First tweet auto-scheduled 2 minutes after deployment
- 📊 FastAPI backend with simple REST API + dashboard
- 🌐 Deployable on **Render** (Free Tier supported)

---

## 📸 Live Demo

🔗 [Twitter Bot](https://twitterbot-bawf.onrender.com/)  

---

## 🧱 Tech Stack

| Layer           | Technology                 |
|------------------|-----------------------------|
| Backend          | FastAPI, APScheduler        |
| AI Integration   | Google Gemini API           |
| Twitter Posting  | Tweepy (OAuth 1.0a)         |
| Database         | SQLAlchemy + SQLite/Postgres|
| Deployment       | Render                      |
| Frontend         | HTML + JS (Static)          |

---

## ⚙️ Environment Setup

### 🔐 Create a `.env` file

```env
# Twitter OAuth 1.0a credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Google Gemini API key
GEMINI_API_KEY=your_gemini_api_key

# Optional: PostgreSQL or SQLite DB
DATABASE_URL=sqlite:///./twitter_bot.db
```

---

## 🚀 Installation

### 1. Clone the repo

```bash
git clone https://github.com/KingVibhor/twitterbot.git
cd ai-twitter-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
uvicorn main:app --host 0.0.0.0 --port=10000
```

---

## 🛠 Project Structure

```
├── main.py                # FastAPI app with scheduler + Gemini + Twitter integration
├── keep_alive.py          # Optional ping file for uptime robot
├── requirements.txt       # Python dependencies
├── static/
│   └── index.html         # Dashboard page
│   └── app.js             # Frontend logic
├── .env                   # Environment variables
└── twitter_bot.db         # SQLite DB (or PostgreSQL via DATABASE_URL)
```

---

## 📡 API Endpoints

| Endpoint                 | Method | Description                        |
|--------------------------|--------|------------------------------------|
| `/`                      | GET    | Serves dashboard HTML              |
| `/app.js`                | GET    | Frontend logic                     |
| `/api/stats`             | GET    | Returns bot stats                  |
| `/api/latest-tweet`      | GET    | Returns latest tweet content       |
| `/api/scheduler-status`  | GET    | Returns tweet status for today     |
| `/api/add-quote`         | POST   | Add & tweet custom quote           |
| `/api/settings`          | POST   | Update post time / hashtags        |

---

## 🧪 Testing

To test Gemini + Twitter manually, use this snippet inside `main.py` or in a script:

```python
import tweepy
import os
import google.generativeai as genai

# Setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-pro")

response = model.generate_content("Give me a short motivational quote with author's name.")
quote = response.text.strip()

print("Generated Quote:", quote)

# Twitter OAuth 1.0a
auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)

api.update_status(quote)
print("Tweeted successfully!")
```

---

## 🧩 Troubleshooting

| Issue                           | Solution                                                                 |
|----------------------------------|--------------------------------------------------------------------------|
| Gemini 404 Error                | Ensure model is `"models/gemini-pro"` and key is valid                   |
| Twitter 403 Error               | Make sure you're using **OAuth 1.0a**, not OAuth2 Bearer Token           |
| Tweet not posted                | Check logs, verify API credentials and access level on [Twitter Portal]  |
| No tweet found (404)            | Wait until first scheduled tweet runs (2 min after deploy)              |
| Not tweeting daily              | Check APScheduler is running in deployed environment                    |

---

## 🧠 Future Enhancements

- Admin panel for quote moderation
- Tweet images using Gemini Vision
- Add logging & retry mechanisms
- Connect to Discord/Telegram for cross-posting
- Add tweet analytics dashboard

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

**Vibhor Kumbhare**  
🌐 [LinkedIn](https://www.linkedin.com/in/vibhor-kumbhare-346763259/)  
💻 [GitHub](https://github.com/KingVibhor)

---

## 🌟 Support

If you found this helpful, drop a ⭐️ on the repo and consider sharing it!