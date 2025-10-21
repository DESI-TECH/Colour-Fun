from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
import os
import asyncio

# ==========================
# CONFIGURATION
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
GAME_URL = "https://colour-fun.vercel.app/game"

app = FastAPI()

# ==========================
# TELEGRAM BOT FUNCTIONS
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
            InlineKeyboardButton("💸 Withdrawal", callback_data="withdrawal")
        ],
        [
            InlineKeyboardButton("👤 Profile", callback_data="profile"),
            InlineKeyboardButton("🎁 Share & Earn", callback_data="share")
        ],
        [InlineKeyboardButton("🎮 Play Game", url=GAME_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎯 Welcome to *Colour-Fun!*\nChoose an option below:", 
                                    reply_markup=reply_markup, parse_mode="Markdown")

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "deposit":
        keyboard = [
            [InlineKeyboardButton("🏦 Bank", callback_data="deposit_bank")],
            [InlineKeyboardButton("💳 UPI", callback_data="deposit_upi")]
        ]
        await query.message.reply_text("💰 Choose your deposit method:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "deposit_bank":
        await query.message.reply_text(
            "🏦 *Bank Deposit Details:*\n\n"
            "Account Holder: John Doe\n"
            "Bank Name: HDFC Bank\n"
            "A/C Number: 1234567890\n"
            "IFSC: HDFC0001234\n\n"
            "📎 Use this to deposit and share the transaction ID with support.",
            parse_mode="Markdown"
        )

    elif data == "deposit_upi":
        await query.message.reply_text(
            "💳 *UPI Deposit Details:*\n\n"
            "UPI ID: colourfun@hdfc\n"
            "Scan the QR or pay directly.\n"
            "Track your deposit using your profile unique code.",
            parse_mode="Markdown"
        )

    elif data == "withdrawal":
        keyboard = [
            [InlineKeyboardButton("🏦 Bank", callback_data="withdraw_bank")],
            [InlineKeyboardButton("💳 UPI", callback_data="withdraw_upi")]
        ]
        await query.message.reply_text("💸 Choose withdrawal method:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "withdraw_bank":
        await query.message.reply_text("🏦 Please enter: Name, Mobile, Bank, Account No, IFSC, Amount (in ₹).")

    elif data == "withdraw_upi":
        await query.message.reply_text("💳 Please enter: Mobile Number, UPI ID (like user@bank), Amount (in ₹).")

    elif data == "profile":
        await query.message.reply_text(
            "👤 *Your Profile*\n\n"
            "Name: Player_001\n"
            "Wallet: ₹1500\n"
            "Points: 1000\n"
            "Bets Played: 20\n\n"
            "Use /transactions to see history.",
            parse_mode="Markdown"
        )

    elif data == "share":
        await query.message.reply_text(
            "🎁 *Share & Earn!*\n\n"
            "Invite friends and earn 100 points (₹10) when they deposit ₹100.\n"
            f"Your referral link:\n👉 https://t.me/{context.bot.username}?start=ref_12345",
            parse_mode="Markdown"
        )

# ==========================
# FASTAPI ROUTES
# ==========================

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("<h2>✅ Colour-Fun FastAPI backend is live!</h2>")

@app.get("/game", response_class=HTMLResponse)
def game_page():
    try:
        with open("game/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Game UI Missing!</h1>")

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await bot_app.process_update(update)
    return JSONResponse({"ok": True})

# ==========================
# BOT INITIALIZATION
# ==========================
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(handle_buttons))
bot = bot_app.bot

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
