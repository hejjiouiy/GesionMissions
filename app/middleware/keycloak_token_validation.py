import os
import httpx
import json
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from jose.utils import base64url_decode
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SimpleKeycloakAuthMiddleware(BaseHTTPMiddleware):
    """
    Simple middleware that validates Keycloak JWT tokens
    Uses local JWKS caching for performance
    """

    def __init__(self, app):
        super().__init__(app)

        # Keycloak configuration - same as your gateway
        self.keycloak_server = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8070")
        self.realm = os.getenv("KEYCLOAK_REALM", "fms")
        self.client_id = os.getenv("KEYCLOAK_CLIENT_ID", "portal")

        # Simple local cache for JWKS
        self.jwks_cache = None
        self.cache_time = 0
        self.cache_duration = 3600  # Cache for 1 hour

        print(f"✅ Auth middleware initialized for Keycloak: {self.keycloak_server}/realms/{self.realm}")

    async def dispatch(self, request: Request, call_next):
        """Main authentication check for every request"""

        # Skip authentication for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            logger.warning("Missing Authorization header")
            raise HTTPException(
                status_code=401,
                detail="Missing Authorization header"
            )

        if not auth_header.startswith("Bearer "):
            logger.warning("Invalid Authorization header format")
            raise HTTPException(
                status_code=401,
                detail="Invalid Authorization header format"
            )

        # Extract the token
        token = auth_header.split(" ")[1]

        try:
            # Validate the token
            user_info = await self._validate_jwt_token(token)

            # Store user info in request for your endpoints to use
            request.state.user = {
                "id": user_info.get("sub"),
                "username": user_info.get("preferred_username"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "roles": user_info.get("realm_access", {}).get("roles", [])
            }

            logger.debug(f"✅ Token validated for user: {user_info.get('preferred_username')}")

        except Exception as e:
            logger.error(f"❌ Token validation failed: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}"
            )

        # Continue to your endpoint
        return await call_next(request)

    async def _validate_jwt_token(self, token: str) -> dict:
        """Validate JWT token using Keycloak's public keys"""

        try:
            # Get the public keys from Keycloak (cached)
            jwks = await self._get_jwks()

            # Extract the key ID from token header
            token_parts = token.split('.')
            if len(token_parts) != 3:
                raise JWTError("Invalid JWT format")

            # Decode the token header to get the key ID
            header_bytes = token_parts[0].encode('ascii')
            header = json.loads(base64url_decode(header_bytes).decode('utf-8'))
            kid = header.get("kid")

            if not kid:
                raise JWTError("Missing key ID in token")

            # Find the matching public key
            public_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    public_key = key
                    break

            if not public_key:
                raise JWTError(f"Public key not found for key ID: {kid}")

            # Validate the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.client_id,
                options={
                    "verify_signature": True,  # Important: verify the signature
                    "verify_exp": True,  # Verify expiration
                    "verify_aud": True  # Verify audience
                }
            )

            return payload

        except JWTError as e:
            raise Exception(f"JWT validation failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Token validation error: {str(e)}")

    async def _get_jwks(self) -> dict:
        """Get JWKS (public keys) from Keycloak with simple caching"""

        current_time = datetime.now().timestamp()

        # Check if we have valid cached JWKS
        if (self.jwks_cache and
                current_time - self.cache_time < self.cache_duration):
            logger.debug("🎯 Using cached JWKS")
            return self.jwks_cache

        # Fetch fresh JWKS from Keycloak
        try:
            logger.info("🔄 Fetching JWKS from Keycloak...")

            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get the OIDC configuration
                oidc_response = await client.get(
                    f"{self.keycloak_server}/realms/{self.realm}/.well-known/openid-configuration"
                )

                if oidc_response.status_code != 200:
                    raise Exception(f"Failed to get OIDC config: {oidc_response.status_code}")

                oidc_config = oidc_response.json()

                # Get the JWKS from the jwks_uri
                jwks_response = await client.get(oidc_config["jwks_uri"])

                if jwks_response.status_code != 200:
                    raise Exception(f"Failed to get JWKS: {jwks_response.status_code}")

                jwks = jwks_response.json()

                # Cache the JWKS
                self.jwks_cache = jwks
                self.cache_time = current_time

                logger.info(f"✅ JWKS cached with {len(jwks.get('keys', []))} keys")
                return jwks

        except Exception as e:
            # If we have old cache, use it as fallback
            if self.jwks_cache:
                logger.warning(f"⚠️ Using stale JWKS cache due to error: {str(e)}")
                return self.jwks_cache

            raise Exception(f"Cannot get JWKS: {str(e)}")


# Helper function for your endpoints
def get_current_user(request: Request) -> dict:
    """
    Get the current authenticated user from request
    Use this in your endpoint functions
    """
    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="User not authenticated")
    return request.state.user