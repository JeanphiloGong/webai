from typing import Optional

from pydantic import BaseModel, ConfigDict


class RegisterRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    code: Optional[str] = None


class LoginRequest(BaseModel):
    identifier: str
    password: str


class UserOut(BaseModel):
    id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    balance: int
    is_activate: bool

    model_config = ConfigDict(from_attributes=True)

class AuthResponse(BaseModel):
    user: UserOut
    token: str
