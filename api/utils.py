import secrets, qrcode, io, base64, json
from datetime import datetime
from .db import SessionLocal, User, Transaction
from .config import BASE_URL

def gen_unique_code(prefix="TX"):
    # 12 character safe code
    return f"{prefix}{secrets.token_hex(6).upper()}"

def gen_qr_base64(data: str):
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return "data:image/png;base64," + b64

def create_transaction(telegram_id: str, type_: str, method: str, details: dict, amount: float):
    db = SessionLocal()
    code = gen_unique_code()
    t = Transaction(code=code, telegram_id=str(telegram_id), type=type_, method=method, details=json.dumps(details), amount=amount, status="pending")
    db.add(t)
    db.commit()
    db.refresh(t)
    db.close()
    return t

def get_transaction(code: str):
    db = SessionLocal()
    t = db.query(Transaction).filter(Transaction.code == code).first()
    db.close()
    return t

def change_transaction_status(code: str, status: str):
    db = SessionLocal()
    t = db.query(Transaction).filter(Transaction.code == code).first()
    if not t:
        db.close()
        return None
    t.status = status
    db.commit()
    db.refresh(t)
    db.close()
    return t

def get_or_create_user(telegram_id, username=None, first_name=None):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    if not user:
        user = User(telegram_id=str(telegram_id), username=username, first_name=first_name)
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()
    return user
