import os
import time
import httpx
from jose import jwt, JWTError
from fastapi.security import HTTPBearer
from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError
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



class AuthMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        # Extract incoming Authorization header
        auth_hdr = context.fastmcp_context._tokens[0]
        print(auth_hdr)
        if not auth_hdr.lower().startswith("bearer "):
            raise ToolError("Unauthorized: Missing Bearer token")
        token = auth_hdr.split(" ", 1)[1].strip()
        # token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9wUmozc1FVUmRZWWo1WVhaRkU3aSJ9.eyJpc3MiOiJodHRwczovL3NtcnV0aS1haS1zb2x1dGlvbi51cy5hdXRoMC5jb20vIiwic3ViIjoicVEwMzRkRnZRWDBRWmhHbm5wVGs5ZDRuN0lhS3EwYkpAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vc21ydXRpLWFpLXNvbHV0aW9uLnVzLmF1dGgwLmNvbS9hcGkvdjIvIiwiaWF0IjoxNzU0NzMyMjk0LCJleHAiOjE3NTQ4MTg2OTQsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyIsImF6cCI6InFRMDM0ZEZ2UVgwUVpoR25ucFRrOWQ0bjdJYUtxMGJKIn0.ema50ciCyahuJs3dbHiPipj5-Eg2dbWZZ6kBldUM9cBQ1GapJQ0DhU1uUDUUQKi178yMsEYjXuCqKFUtp5nMAjyxPcIXiSQRAyDk522J0FIK1dEx8CPkiHnLdM3QcFsiw1Z8eZ6ZgWHATfM7rubuaU8Z-NmB4XYM5e2Cl36uYrLGpGFM6xgJotil66HSq5wDMuNaGbiYN2coaaIjBXye4kJunKomxJWgVYfkOflPzWiXV0NE-AxD5MJQNetu6-DrWTQS--YKdzR7pBRHJoW_fJSB-7RngQKnEUm9NE-fwfLVLCA3QelouSxdsRBRyIZvKdATmP8c86cpJtj-lipfOQ"

        # Verify JWT
        jwks = await jwks_client.get_jwks()
        try:
            jwt.decode(token, jwks, algorithms=["RS256"], audience=OAUTH_AUDIENCE, issuer=OAUTH_ISSUER)
        except JWTError:
            raise ToolError("Unauthorized: Invalid token")

        return await call_next(context)

# Initialize server
mcp = FastMCP("Secure Server")
mcp.add_middleware(AuthMiddleware())

# Define protected tool
@mcp.tool()
def add_numbers(a: float, b: float) -> dict:
    """Add two numbers, protected by JWT auth."""
    return {"result": a + b}

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
