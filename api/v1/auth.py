"""Authentication API endpoints."""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    PasswordChange,
    PasswordResetRequest,
    PasswordReset,
)
from models.user import User
from models.enums import UserRole
from services.auth_service import AuthService
from utils.security import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Register a new user (admin only).

    Args:
        user_data: User registration data
        db: Database session
        current_user: Current authenticated user (must be admin)

    Returns:
        Created user

    Raises:
        HTTPException: If user is not admin or registration fails
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"Unauthorized registration attempt by {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can register new users",
        )

    try:
        service = AuthService(db)
        user = await service.register_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=UserRole(user_data.role),
        )
        return UserResponse.from_orm(user)
    except ValueError as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Login with email and password.

    Args:
        credentials: Email and password
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    try:
        service = AuthService(db)
        user = await service.authenticate(
            email=credentials.email,
            password=credentials.password,
        )

        if not user:
            logger.warning(f"Failed login attempt for {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        tokens = await service.generate_tokens(user)
        user_response = UserResponse.from_orm(user)

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=user_response,
            expires_in=86400,  # 24 hours in seconds
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_token: str = Query(..., description="Refresh token"),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token.

    Args:
        refresh_token: Refresh token from login
        db: Database session

    Returns:
        New access token

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        service = AuthService(db)
        tokens = await service.refresh_token(refresh_token)

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=refresh_token,  # Return same refresh token
            token_type=tokens["token_type"],
            expires_in=86400,
        )
    except ValueError as e:
        logger.warning(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current authenticated user profile.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user information
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_profile(
    profile_update: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Update user profile.

    Args:
        profile_update: Profile update data (first_name, last_name, metadata)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated user

    Raises:
        HTTPException: If update fails
    """
    try:
        service = AuthService(db)
        user = await service.update_user_profile(
            user_id=current_user.id,
            first_name=profile_update.get("first_name"),
            last_name=profile_update.get("last_name"),
            metadata=profile_update.get("metadata"),
        )
        return UserResponse.from_orm(user)
    except ValueError as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed",
        )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Change user password.

    Args:
        password_data: Old and new password
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: If password change fails
    """
    try:
        service = AuthService(db)
        await service.change_password(
            user_id=current_user.id,
            old_password=password_data.old_password,
            new_password=password_data.new_password,
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Password change failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed",
        )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Request password reset by email.

    Args:
        reset_request: Email address
        db: Database session

    Returns:
        Success message (doesn't reveal if email exists)
    """
    try:
        service = AuthService(db)
        reset_token = await service.request_password_reset(reset_request.email)

        # In production, send email with reset link containing token
        if reset_token:
            # Example: send_email(reset_request.email, "Password Reset", reset_token)
            logger.info(f"Password reset requested for {reset_request.email}")

        # Always return same message for security
        return {
            "message": "If an account exists for this email, you will receive a password reset link"
        }
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed",
        )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Reset password with reset token.

    Args:
        reset_data: Email, reset token, and new password
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If password reset fails
    """
    try:
        service = AuthService(db)
        await service.reset_password(
            email=reset_data.email,
            reset_token=reset_data.token,
            new_password=reset_data.new_password,
        )
        return {"message": "Password reset successfully"}
    except ValueError as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Password reset failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed",
        )


@router.get("/users", status_code=status.HTTP_200_OK)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """List all users (admin only).

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of users

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"Unauthorized users list attempt by {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can list users",
        )

    try:
        service = AuthService(db)
        users, total = await service.get_all_users(skip=skip, limit=limit)
        return {
            "users": [UserResponse.from_orm(user) for user in users],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users",
        )
