import os
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()
SECRET = os.getenv("INTERNAL_JWT_SECRET")

class VerifyInternalJWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("X-Internal-Gateway-Key")
        if not token:
            raise HTTPException(status_code=403, detail="Missing gateway token")
        try:
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])
            if payload.get("iss") != "api-gateway":
                raise HTTPException(status_code=403, detail="Invalid issuer")
        except JWTError as e:
            raise HTTPException(status_code=403, detail=f"Invalid or expired token: {str(e)}")

        return await call_next(request)
