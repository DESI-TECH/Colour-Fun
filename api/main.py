from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.ext import MessageHandler, filters
import asyncio

app = FastAPI()

# ---------------- TELEGRAM BOT SETUP ----------------
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Vercel deployment URL

bot_app = Application.builder().token(TOKEN).build()

# --- Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            {"text": "💰 Deposit", "callback_data": "deposit"},
            {"text": "🏦 Withdraw", "callback_data": "withdraw"},
        ],
        [
            {"text": "👤 Profile", "callback_data": "profile"},
            {"text": "🎁 Share & Earn", "callback_data": "share"},
        ],
        [{"text": "🎮 Play Game", "web_app": {"url": f"{WEBHOOK_URL}/game"}}],
    ]
    reply_markup = {"inline_keyboard": keyboard}
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to the Game Bot! Choose an option below 👇",
        reply_markup=reply_markup,
    )

bot_app.add_handler(CommandHandler("start", start))

# ---------------- WEBHOOK ROUTE ----------------
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}

# ---------------- GAME ROUTE ----------------
@app.get("/game", response_class=HTMLResponse)
async def get_game():
    with open("game/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# ---------------- HEALTH CHECK ----------------
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Bot + Game running fine"}
