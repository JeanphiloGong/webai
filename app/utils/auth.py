# app/utils/auth.py

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jwt import algorithms
from typing_extensions import deprecated
import jwt
from passlib.context import CryptContext

from config import JWT_ALGORITHM, JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

# 对密码进行验证
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 获取密码的hash值
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 创建访问token
def create_access_token(
        data: dict[str, Any],
        expires_delta: Optional[timedelta] = None,
        ):
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encode_jwt

# 解码访问token
def decode_access_token(token: str) -> Dict[str, Any]:
    """
    解码并校验 Access Token, 失败的时候就抛 ValueError
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")



