from fastapi import Depends, HTTPException, Header, APIRouter, status
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from internal.models import User, Transaction
from internal.db_init import get_db
from routers.schemas.login import AuthResponse, LoginRequest, RegisterRequest, UserOut
from utils.auth import create_access_token, decode_access_token, get_password_hash, verify_password

router = APIRouter()

INITIAL_SIGNUP_BOUNS = 1000

def get_current_user(
        db: Session = Depends(get_db),
        authorization: str | None = Header(default=None, alias="Authorization"),
        ) -> User:
    if not authorization:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="not authenticated",
                )
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="invalid authorization header",
                    )


        try:
            payload = decode_access_token(token)
        except ValueError:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    )

        user_id_str = str(payload.get("sub", ""))
        if not user_id_str.isdigit():
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    defail="Invalid token payload",
                    )

        user = db.query(User).filter(User.id == int(user_id_str)).first()
        if not user:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    )
        return user


@router.post("/api/auth/register", response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if not payload.email and not payload.phone:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="email 或 phone 至少提供一个",
                )

    # 检查是否存在同邮箱或者同个手号码的用户
    query = db.query(User)
    if payload.email:
        existing = query.filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail = "该邮箱已注册",
                    )
    if payload.phone:
        existing = query.filter(User.phone == payload.phone).first()
        if existing:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该手机号已经注册",
                    )

    hashed_password = get_password_hash(payload.password)
    user = User(
            email=payload.email,
            phone=payload.phone,
            password_hash=hashed_password,
            balance=0,
            is_activate=True,
            )
    db.add(user)
    db.flush()

    # 注册赠送获取 + 记录交易
    bouns = INITIAL_SIGNUP_BOUNS
    user.balance += bouns
    tx = Transaction(
            user_id = user.id,
            amount=bouns,
            type="reward",
            reason="signup_bouns",
            )
    db.add(tx)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return AuthResponse(user=user, token=token)


#############################
# 登录接口
#############################
@router.post("/api/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    identifier = payload.identifier

    user = (
            db.query(User)
            .filter(
                (User.email == identifier) | (User.phone == identifier)
                )
            .first()
            )
    
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="帐号或者密码错误",
                )

    if not user.is_activate:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户已被禁用",
                )
    token = create_access_token({"sub": str(user.id)})

    return AuthResponse(user=user, token=token)

#####################
# 获取当前用户信息
#######################
@router.get("/api/auth/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
