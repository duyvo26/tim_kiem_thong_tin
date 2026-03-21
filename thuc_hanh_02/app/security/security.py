# app/security/security.py

from fastapi import Header, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.config import settings

from fastapi import Security  # noqa: E402
from fastapi.security import APIKeyHeader  # noqa: E402

# === Config ===
API_KEY = settings.API_KEY
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


# Xác định header `Authorization`
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


async def verify_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != f"Bearer {settings.API_KEY}":
        raise HTTPException(status_code=403, detail="API Key không hợp lệ!")
    return api_key_header


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ✅ Xác thực JWT (dù có đăng nhập hay không)
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # return payload chứa: sub, role, v.v.
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc hết hạn",
        )
