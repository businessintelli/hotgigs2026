"""Authentication service for user management and token generation."""

import logging
import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.user import User
from models.enums import UserRole
from utils.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token

logger = logging.getLogger(__name__)

# Password strength requirements
MIN_PASSWORD_LENGTH = 8
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_NUMBERS = True
REQUIRE_SPECIAL = True


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        """Initialize auth service.

        Args:
            db: Async database session
        """
        self.db = db

    async def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: UserRole = UserRole.VIEWER,
    ) -> User:
        """Register a new user.

        Args:
            email: User email address
            password: Plain text password
            first_name: User first name
            last_name: User last name
            role: User role (default: VIEWER)

        Returns:
            Created user object

        Raises:
            ValueError: If email already exists or password is weak
        """
        # Validate email format
        if not self._is_valid_email(email):
            raise ValueError("Invalid email format")

        # Check if email already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # Validate password strength
        password_issues = self._validate_password_strength(password)
        if password_issues:
            raise ValueError(f"Password is too weak: {', '.join(password_issues)}")

        # Hash password
        hashed_password = hash_password(password)

        # Create user
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=True,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"User registered: {email} with role {role}")
        return user

    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> Optional[User]:
        """Authenticate user with email and password.

        Args:
            email: User email address
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = await self.get_user_by_email(email)
        if not user or not user.is_active:
            logger.warning(f"Authentication failed for {email}: user not found or inactive")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed for {email}: invalid password")
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        self.db.add(user)
        await self.db.commit()

        logger.info(f"User authenticated: {email}")
        return user

    async def generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate access and refresh tokens for a user.

        Args:
            user: User object

        Returns:
            Dictionary with access_token and refresh_token
        """
        access_token = create_access_token(
            subject=str(user.id),
            additional_claims={
                "email": user.email,
                "role": user.role,
                "name": user.full_name,
            },
        )

        refresh_token = create_refresh_token(str(user.id))

        logger.info(f"Tokens generated for user {user.id}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh access token using a refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            Dictionary with new access_token, or None if refresh token is invalid

        Raises:
            ValueError: If token is invalid or user not found
        """
        token_data = verify_token(refresh_token)
        if not token_data or token_data.get("type") != "refresh":
            logger.warning("Invalid refresh token")
            raise ValueError("Invalid refresh token")

        user_id = int(token_data.get("sub"))
        user = await self.get_user_by_id(user_id)

        if not user or not user.is_active:
            logger.warning(f"Refresh failed: user {user_id} not found or inactive")
            raise ValueError("User not found or inactive")

        # Generate new access token
        access_token = create_access_token(
            subject=str(user.id),
            additional_claims={
                "email": user.email,
                "role": user.role,
                "name": user.full_name,
            },
        )

        logger.info(f"Access token refreshed for user {user_id}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    async def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
    ) -> User:
        """Change user password.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            Updated user object

        Raises:
            ValueError: If old password is wrong or new password is weak
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Verify old password
        if not verify_password(old_password, user.hashed_password):
            logger.warning(f"Password change failed for user {user_id}: incorrect old password")
            raise ValueError("Incorrect old password")

        # Validate new password strength
        password_issues = self._validate_password_strength(new_password)
        if password_issues:
            raise ValueError(f"New password is too weak: {', '.join(password_issues)}")

        # Update password
        user.hashed_password = hash_password(new_password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Password changed for user {user_id}")
        return user

    async def request_password_reset(self, email: str) -> Optional[str]:
        """Request password reset by email.

        Args:
            email: User email address

        Returns:
            Reset token if user found, None otherwise
        """
        user = await self.get_user_by_email(email)
        if not user:
            # Don't reveal if email exists
            logger.info(f"Password reset requested for non-existent email: {email}")
            return None

        # Generate reset token (valid for 1 hour)
        reset_token = secrets.token_urlsafe(32)
        reset_token_hash = hash_password(reset_token)
        reset_expires = datetime.utcnow() + timedelta(hours=1)

        # Store in metadata
        user.extra_metadata = user.extra_metadata or {}
        user.extra_metadata["password_reset_token"] = reset_token_hash
        user.extra_metadata["password_reset_expires"] = reset_expires.isoformat()

        self.db.add(user)
        await self.db.commit()

        logger.info(f"Password reset requested for user {user.id}")
        return reset_token

    async def reset_password(self, email: str, reset_token: str, new_password: str) -> User:
        """Reset password using reset token.

        Args:
            email: User email address
            reset_token: Password reset token
            new_password: New password

        Returns:
            Updated user object

        Raises:
            ValueError: If token is invalid, expired, or password is weak
        """
        user = await self.get_user_by_email(email)
        if not user:
            raise ValueError("User not found")

        # Check reset token
        metadata = user.extra_metadata or {}
        stored_token_hash = metadata.get("password_reset_token")
        reset_expires_str = metadata.get("password_reset_expires")

        if not stored_token_hash or not reset_expires_str:
            raise ValueError("No password reset request found")

        # Verify token
        if not verify_password(reset_token, stored_token_hash):
            logger.warning(f"Invalid reset token for user {user.id}")
            raise ValueError("Invalid reset token")

        # Check expiration
        reset_expires = datetime.fromisoformat(reset_expires_str)
        if datetime.utcnow() > reset_expires:
            logger.warning(f"Reset token expired for user {user.id}")
            raise ValueError("Reset token has expired")

        # Validate new password strength
        password_issues = self._validate_password_strength(new_password)
        if password_issues:
            raise ValueError(f"New password is too weak: {', '.join(password_issues)}")

        # Update password and clear reset token
        user.hashed_password = hash_password(new_password)
        user.extra_metadata.pop("password_reset_token", None)
        user.extra_metadata.pop("password_reset_expires", None)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Password reset completed for user {user.id}")
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object or None
        """
        stmt = select(User).where(User.id == user_id).where(User.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: User email address

        Returns:
            User object or None
        """
        stmt = select(User).where(User.email == email.lower()).where(User.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> Tuple[list, int]:
        """Get all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            Tuple of (users list, total count)
        """
        # Get total count
        count_stmt = select(User).where(User.is_active == True)
        count_result = await self.db.execute(count_stmt)
        total = len(count_result.scalars().all())

        # Get paginated results
        stmt = select(User).where(User.is_active == True).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        users = result.scalars().all()

        return users, total

    async def update_user_profile(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> User:
        """Update user profile information.

        Args:
            user_id: User ID
            first_name: New first name
            last_name: New last name
            metadata: Updated metadata

        Returns:
            Updated user object

        Raises:
            ValueError: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if metadata:
            user.extra_metadata = user.extra_metadata or {}
            user.extra_metadata.update(metadata)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Profile updated for user {user_id}")
        return user

    async def deactivate_user(self, user_id: int) -> User:
        """Deactivate a user account.

        Args:
            user_id: User ID

        Returns:
            Deactivated user object

        Raises:
            ValueError: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        user.is_active = False
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"User deactivated: {user_id}")
        return user

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def _validate_password_strength(password: str) -> list[str]:
        """Validate password strength.

        Args:
            password: Password to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        if len(password) < MIN_PASSWORD_LENGTH:
            issues.append(f"Must be at least {MIN_PASSWORD_LENGTH} characters")

        if REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            issues.append("Must contain at least one uppercase letter")

        if REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            issues.append("Must contain at least one lowercase letter")

        if REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            issues.append("Must contain at least one number")

        if REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Must contain at least one special character")

        return issues
