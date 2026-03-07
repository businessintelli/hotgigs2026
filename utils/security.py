"""Security utilities — password hashing, JWT tokens with multi-tenant claims."""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a JWT access token with optional multi-tenant claims.
    
    Standard claims: sub, exp
    Tenant claims (via additional_claims):
      - organization_id: int
      - organization_type: str (msp/client/supplier)
      - role_in_org: str
      - accessible_org_ids: List[int]
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiry_hours)

    to_encode = {"sub": subject}

    if additional_claims:
        to_encode.update(additional_claims)

    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    return encoded_jwt


def create_tenant_token(
    user_id: int,
    organization_id: int,
    organization_type: str,
    role_in_org: str,
    accessible_org_ids: Optional[List[int]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT token with full multi-tenant claims.
    Used when user logs in or switches organizations.
    """
    claims = {
        "organization_id": organization_id,
        "organization_type": organization_type,
        "role_in_org": role_in_org,
    }
    if accessible_org_ids:
        claims["accessible_org_ids"] = accessible_org_ids

    return create_access_token(
        subject=str(user_id),
        expires_delta=expires_delta,
        additional_claims=claims,
    )


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return its claims."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        logger.error(f"Invalid token: {str(e)}")
        return None


def create_refresh_token(subject: str) -> str:
    """Create a JWT refresh token."""
    expires_delta = timedelta(days=settings.jwt_refresh_expiry_days)
    return create_access_token(subject, expires_delta, {"type": "refresh"})
