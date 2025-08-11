import os
import httpx
import time
from jose import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

OAUTH_ISSUER = os.getenv("OAUTH_ISSUER")
OAUTH_AUDIENCE = os.getenv("OAUTH_AUDIENCE")
JWKS_URL = os.getenv("OAUTH_JWKS_URL")

if not all([OAUTH_ISSUER, OAUTH_AUDIENCE, JWKS_URL]):
    raise RuntimeError("Missing OAuth environment variables")

security = HTTPBearer()

class JWKSClient:
    def __init__(self, url: str):
        self.url = url
        self._jwks = None
        self._expires = 0

    async def get_jwks(self):
        if self._jwks and self._expires > time.time():
            return self._jwks
        async with httpx.AsyncClient() as client:
            r = await client.get(self.url)
            r.raise_for_status()
            self._jwks = r.json()
            self._expires = time.time() + 3600
            return self._jwks

jwks_client = JWKSClient(JWKS_URL)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    jwks = await jwks_client.get_jwks()
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=OAUTH_AUDIENCE,
            issuer=OAUTH_ISSUER,
            options={"verify_at_hash": False},
        )
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload
