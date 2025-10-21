from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)
import asyncio
import os

# =======================
# 🔧 Basic Configurations
# =======================

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
GAME_URL = "https://your-vercel-game-url.vercel.app/game"  # change to your actual vercel domain

app = FastAPI()


# =======================
# 🤖 Telegram Bot Setup
# =======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
         InlineKeyboardButton("💸 Withdrawal", callback_data="withdrawal")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile"),
         InlineKeyboardButton("🎁 Share & Earn", callback_data="share")],
        [InlineKeyboardButton("🎮 Play", url=GAME_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to the Game Bot 🎯\nChoose an option below:", reply_markup=reply_markup)


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "deposit":
        keyboard = [
            [InlineKeyboardButton("🏦 Bank", callback_data="deposit_bank")],
            [InlineKeyboardButton("💳 UPI", callback_data="deposit_upi")]
        ]
        await query.message.reply_text(
            "💰 Choose your deposit method:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "deposit_bank":
        await query.message.reply_text(
            "🏦 Bank Details for Deposit:\n\n"
            "Account Holder: John Doe\n"
            "Bank: HDFC Bank\n"
            "A/C Number: 1234567890\n"
            "IFSC: HDFC0001234\n\n"
            "Use this account to deposit funds and share the transaction ID with support."
        )

    elif query.data == "deposit_upi":
        await query.message.reply_text(
            "💳 UPI Deposit Details:\n\n"
            "UPI ID: game@hdfc\n"
            "Scan this QR to pay and funds will reflect automatically.\n"
            "Track your payment using your unique code on your profile."
        )

    elif query.data == "withdrawal":
        keyboard = [
            [InlineKeyboardButton("🏦 Bank", callback_data="withdraw_bank")],
            [InlineKeyboardButton("💳 UPI", callback_data="withdraw_upi")]
        ]
        await query.message.reply_text(
            "💸 Choose your withdrawal method:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "withdraw_bank":
        await query.message.reply_text(
            "🏦 Please send the following details one by one:\n"
            "1️⃣ Bank Account Holder Name\n"
            "2️⃣ Mobile Number\n"
            "3️⃣ Bank Name\n"
            "4️⃣ Account Number\n"
            "5️⃣ IFSC Code\n"
            "6️⃣ Amount to Withdraw"
        )

    elif query.data == "withdraw_upi":
        await query.message.reply_text(
            "💳 Please send the following details one by one:\n"
            "1️⃣ Mobile Number\n"
            "2️⃣ UPI ID (e.g., user@bank)\n"
            "3️⃣ Amount to Withdraw"
        )

    elif query.data == "profile":
        await query.message.reply_text(
            "👤 Your Profile\n\n"
            "Name: Player_001\n"
            "Wallet Balance: ₹1500\n"
            "Total Bets: 25\n"
            "Points: 1200\n\n"
            "Use /transactions to view full history."
        )

    elif query.data == "share":
        await query.message.reply_text(
            "🎁 *Share & Earn!*\n\n"
            "Invite friends to join and earn 100 points (worth ₹10) when they deposit ₹100.\n"
            "Share your referral link below 👇\n\n"
            f"https://t.me/{context.bot.username}?start=ref_12345",
            parse_mode="Markdown"
        )


# =======================
# 🌐 FastAPI Web Endpoints
# =======================

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("<h2>✅ FastAPI Telegram Game Bot is Live</h2>")


@app.get("/game", response_class=HTMLResponse)
def game_page():
    # serve your HTML file
    try:
        with open("game/index.html", "r", encoding="utf-8") as f:
            html = f.read()
        return HTMLResponse(content=html)
    except FileNotFoundError:
        return HTMLResponse("<h1>Game UI Not Found</h1>")


@app.post("/webhook")
async def webhook(request: Request):
    """Telegram webhook endpoint for Vercel"""
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return JSONResponse({"ok": True})


# =======================
# 🚀 Bot Initialization
# =======================

application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_buttons))

bot = application.bot


# ================
# 🧠 Local Testing
# ================
if __name__ == "__main__":
    import uvicorn
    print("🚀 Running locally at http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
