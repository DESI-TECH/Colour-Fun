from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import os

app = FastAPI()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

keyboard = [
    [InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
     InlineKeyboardButton("🏧 Withdrawal", callback_data="withdrawal")],
    [InlineKeyboardButton("👤 Profile", callback_data="profile"),
     InlineKeyboardButton("📤 Share & Earn", callback_data="share")],
    [InlineKeyboardButton("🎮 Play", callback_data="play")]
]

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    text = data.get("message", {}).get("text", "")

    if chat_id and text == "/start":
        await bot.send_message(
            chat_id=chat_id,
            text="Welcome to Colour-Fun! Choose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    return JSONResponse({"ok": True})
