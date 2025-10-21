import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8397950433:AAEGOSrx1_a3XWVMpifv8Z_WFj1oqZ0HRXk")
BASE_URL = os.environ.get("BASE_URL", "https://your-vercel-domain.vercel.app")  # used to build track links
WEBHOOK_PATH = "./api/webhook"
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data.db")
ADMIN_CHAT_ID = os.environ.get("6206420660")  # optional admin to notify
