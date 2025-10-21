from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
import os
import logging

# --------------------------
# FASTAPI APP
# --------------------------
app = FastAPI(title="Colour-Fun Backend")

# --------------------------
# TELEGRAM BOT CONFIG
# --------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# --------------------------
# IN-MEMORY USER STORAGE
# --------------------------
users = {}  # {chat_id: {"balance": int, "points": int, "transactions": []}}

logging.basicConfig(level=logging.INFO)

# --------------------------
# TELEGRAM COMMANDS
# --------------------------
def start(update, context):
    chat_id = update.effective_chat.id
    if chat_id not in users:
        users[chat_id] = {"balance": 0, "points": 0, "transactions": []}
    
    # Inline keyboard layout (in-chat buttons)
    keyboard = [
        [InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
         InlineKeyboardButton("🏧 Withdrawal", callback_data="withdrawal")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile"),
         InlineKeyboardButton("📤 Share & Earn", callback_data="share")],
        [InlineKeyboardButton("🎮 Play", callback_data="play")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(
        chat_id=chat_id,
        text="Welcome to Colour-Fun! Choose an option:",
        reply_markup=reply_markup
    )

# --------------------------
# BUTTON CALLBACK LOGIC
# --------------------------
def button_callback(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    data = query.data
    query.answer()
    
    if data == "deposit":
        keyboard = [
            [InlineKeyboardButton("🏦 Bank", callback_data="deposit_bank")],
            [InlineKeyboardButton("📱 UPI", callback_data="deposit_upi")]
        ]
        query.edit_message_text("Choose deposit method:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "withdrawal":
        keyboard = [
            [InlineKeyboardButton("🏦 Bank", callback_data="withdraw_bank")],
            [InlineKeyboardButton("📱 UPI", callback_data="withdraw_upi")]
        ]
        query.edit_message_text("Choose withdrawal method:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "profile":
        user = users.get(chat_id, {"balance": 0, "points": 0, "transactions": []})
        msg = (f"👤 Profile:\n"
               f"Balance: ₹{user['balance']}\n"
               f"Points: {user['points']}\n"
               f"Transactions: {len(user['transactions'])}")
        query.edit_message_text(msg)
    
    elif data == "share":
        share_msg = ("📤 Share & Earn:\n"
                     "Invite friends using your unique code. When a friend deposits ₹100, "
                     "you earn 100 points (100 points = ₹10).")
        query.edit_message_text(share_msg)
    
    elif data == "play":
        # Link to FastAPI game page
        game_url = os.getenv("GAME_URL", "/game")
        query.edit_message_text(f"🎮 Launching the game: [Play Now]({game_url})", parse_mode='Markdown')

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button_callback))

# --------------------------
# FASTAPI ROUTES
# --------------------------
@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI backend is live!"}

@app.get("/game", response_class=HTMLResponse)
def serve_game():
    try:
        with open("game/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Game not found</h1>", status_code=404)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Receive Telegram updates via webhook"""
    update_data = await request.json()
    update = Update.de_json(update_data, bot)
    dispatcher.process_update(update)
    return JSONResponse({"ok": True, "received": update_data})

# --------------------------
# HEALTH CHECK
# --------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy"}
