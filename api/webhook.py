from fastapi import FastAPI, Request, BackgroundTasks, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import httpx, os, json
from .config import BOT_TOKEN, BASE_URL, ADMIN_CHAT_ID
from .utils import gen_qr_base64, create_transaction, get_transaction, change_transaction_status, get_or_create_user
from .db import init_db

app = FastAPI()
init_db()

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def telegram_api(method: str, payload: dict):
    url = f"{TELEGRAM_API}/{method}"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(url, json=payload)
    return r.json()

def build_main_keyboard(webapp_url: str):
    # Inline keyboard with Web App (Play) and other inline buttons using callback_data
    keyboard = {
        "inline_keyboard": [
            [
                {"text":"💰 Deposit", "callback_data":"deposit_menu"},
                {"text":"💸 Withdrawal", "callback_data":"withdraw_menu"}
            ],
            [
                {"text":"👤 Profile", "callback_data":"profile"},
                {"text":"🔁 Share & Earn", "callback_data":"share_earn"}
            ],
            [
                {"text":"🎮 Play", "web_app": {"url": webapp_url}}
            ]
        ]
    }
    return keyboard

@app.post("/api/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    # handle updates
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text","")
        if text == "/start":
            # create user
            user = msg.get("from",{})
            get_or_create_user(telegram_id=user["id"], username=user.get("username"), first_name=user.get("first_name"))
            webapp_url = f"{BASE_URL}/game/index.html?tg_user={chat_id}"
            keyboard = build_main_keyboard(webapp_url)
            await telegram_api("sendMessage", {"chat_id": chat_id, "text":"Welcome! Use the buttons below:", "reply_markup": keyboard})
            return JSONResponse({"ok": True})
    # handle callback_query (button clicks)
    if "callback_query" in data:
        cq = data["callback_query"]
        action = cq["data"]
        chat_id = cq["from"]["id"]
        message_id = cq["message"]["message_id"]
        # simple dispatcher
        if action == "deposit_menu":
            # show Bank or UPI options
            keyboard = {"inline_keyboard":[[{"text":"🏦 Bank","callback_data":"deposit_bank"},{"text":"🔗 UPI","callback_data":"deposit_upi"}]]}
            await telegram_api("answerCallbackQuery", {"callback_query_id": cq["id"], "text":"Choose deposit method","show_alert":False})
            await telegram_api("sendMessage", {"chat_id": chat_id, "text":"Choose deposit method:", "reply_markup": keyboard})
            return JSONResponse({"ok": True})
        if action == "deposit_bank":
            # send bank details + generate tracking code
            code = create_transaction(chat_id, "deposit", "bank", {"info":"bank deposit requested"}, 0.0).code
            bank_details = ("Bank A/C Name: YOUR NAME\nBank: BANK NAME\nA/C No: 0000000000\nIFSC: ABCD0123456\n\n"
                            f"Use tracking code: {code}\nTrack here: {BASE_URL}/api/track/{code}")
            await telegram_api("answerCallbackQuery", {"callback_query_id": cq["id"], "text":"Bank details sent.","show_alert": False})
            await telegram_api("sendMessage", {"chat_id": chat_id, "text": bank_details})
            return JSONResponse({"ok": True})
        if action == "deposit_upi":
            # send UPI details + QR image
            code_obj = create_transaction(chat_id, "deposit", "upi", {"upi":"user@bank"}, 0.0)
            code = code_obj.code
            upi_uri = "upi://pay?pn=Your+Name&pa=user@bank&am=&cu=INR"
            qr_b64 = gen_qr_base64(upi_uri)
            caption = f"UPI: user@bank\nTracking code: {code}\nTrack: {BASE_URL}/api/track/{code}"
            await telegram_api("sendPhoto", {"chat_id": chat_id, "photo": qr_b64, "caption": caption})
            return JSONResponse({"ok": True})

        if action == "withdraw_menu":
            keyboard = {"inline_keyboard":[[{"text":"🏦 Bank","callback_data":"withdraw_bank"},{"text":"🔗 UPI","callback_data":"withdraw_upi"}]]}
            await telegram_api("answerCallbackQuery", {"callback_query_id": cq["id"], "text":"Choose withdrawal method","show_alert":False})
            await telegram_api("sendMessage", {"chat_id": chat_id, "text":"Choose withdrawal method:", "reply_markup": keyboard})
            return JSONResponse({"ok": True})

        if action == "profile":
            # fetch user
            from .db import SessionLocal, User
            db = SessionLocal()
            user = db.query(User).filter(User.telegram_id == str(chat_id)).first()
            db.close()
            if not user:
                await telegram_api("sendMessage", {"chat_id": chat_id, "text":"Profile not found. Use /start to register."})
            else:
                text = (f"👤 Profile\nName: {user.first_name or user.username}\nWallet balance: ₹{user.wallet_balance:.2f}\n"
                        f"Points: {user.points}\n")
                # transaction history quick link: we can display last 10
                await telegram_api("sendMessage", {"chat_id": chat_id, "text": text})
            return JSONResponse({"ok": True})

        if action == "share_earn":
            code = f"REF{chat_id}"
            text = (f"🔗 Share & Earn\nInvite link: {BASE_URL}/game/index.html?ref={code}\n"
                    "Reward: 100 points (convertible: 100 points = ₹10) when the referred user deposits ₹100.\nShare this link with friends.")
            await telegram_api("answerCallbackQuery", {"callback_query_id": cq["id"], "text":"Share & Earn info sent"})
            await telegram_api("sendMessage", {"chat_id": chat_id, "text": text})
            return JSONResponse({"ok": True})

    return JSONResponse({"ok": True})
