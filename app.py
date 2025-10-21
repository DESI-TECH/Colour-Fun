import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

app = FastAPI()

# Serve static files from /game folder
app.mount("/static", StaticFiles(directory="game"), name="static")

# Telegram bot setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

# Inline keyboard layout
keyboard = [
    [
        InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
        InlineKeyboardButton("🏧 Withdrawal", callback_data="withdrawal")
    ],
    [
        InlineKeyboardButton("👤 Profile", callback_data="profile"),
        InlineKeyboardButton("📤 Share & Earn", callback_data="share")
    ],
    [
        InlineKeyboardButton("🎮 Play", callback_data="play")
    ]
]

@app.get("/")
async def root():
    return {"status": "ok", "message": "FastAPI backend live!"}

@app.get("/game", response_class=HTMLResponse)
async def serve_game():
    path = "game/index.html"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>Game not found</h1>", status_code=404)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    chat_id = None
    text = None

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text")
    elif "callback_query" in data:
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        text = data["callback_query"]["data"]

    # Respond to /start command
    if chat_id and text == "/start":
        await bot.send_message(
            chat_id=chat_id,
            text="Welcome to Colour-Fun! Choose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    return JSONResponse({"ok": True})
