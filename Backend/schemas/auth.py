from pydantic import BaseModel, EmailStr


# =========================================================
# LOGIN REQUEST
# Data received from Login frontend
# =========================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =========================================================
# LOGIN RESPONSE
# Returned after successful authentication
# =========================================================

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    name: str
    email: EmailStr