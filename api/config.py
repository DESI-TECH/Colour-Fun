import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "<PUT_TOKEN_HERE>")
BASE_URL = os.environ.get("BASE_URL", "https://your-vercel-domain.vercel.app")  # used to build track links
WEBHOOK_PATH = f"/api/webhook"
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data.db")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")  # optional admin to notify
