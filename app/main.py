from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import text
from internal.db_init import get_db

from routers import user

app = FastAPI(
        title="GameCoin Platform"
        )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "ok"}

app.include_router(user.router, prefix="", tags=["用户登录操作"])
