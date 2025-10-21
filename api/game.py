from fastapi import Query

@app.get("/api/game/profile")
def game_profile(tg_id: str = Query(...)):
    from .db import SessionLocal, User
    db = SessionLocal()
    u = db.query(User).filter(User.telegram_id == str(tg_id)).first()
    db.close()
    if not u:
        return JSONResponse({"ok": False, "error":"not found"}, status_code=404)
    return {"ok": True, "profile": {"wallet_balance": u.wallet_balance, "points": u.points, "username": u.username or u.first_name}}

@app.post("/api/game/place_bet")
async def place_bet(request: Request):
    data = await request.json()
    tg_id = str(data.get("tg_id"))
    amount = float(data.get("amount", 0))
    choice = data.get("choice")  # e.g., "red" or number
    # check wallet
    from .db import SessionLocal, User
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == tg_id).first()
    if not user:
        db.close()
        return JSONResponse({"ok": False, "error": "user not found"})
    if user.wallet_balance < amount:
        db.close()
        return JSONResponse({"ok": False, "error":"insufficient balance"})
    # lock funds (simple)
    user.wallet_balance -= amount
    # record bet as a transaction (type bet)
    from .utils import create_transaction
    tx = create_transaction(tg_id, "bet", "game", {"choice": choice}, amount)
    db.add(user)
    db.commit()
    db.close()
    # return success so UI shows bet placed
    return {"ok": True, "tx_code": tx.code}
