from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, Dict, Any
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Configuration
    app_name: str = Field(default="HR Automation Platform")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Database Configuration
    database_url: str = Field(default="postgresql+asyncpg://hr_user:hr_password@localhost:5432/hr_platform")
    database_sync_url: str = Field(default="postgresql://hr_user:hr_password@localhost:5432/hr_platform")
    database_pool_size: int = Field(default=20)
    database_max_overflow: int = Field(default=10)
    database_pool_recycle: int = Field(default=3600)
    database_echo: bool = Field(default=False)

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0")

    # RabbitMQ Configuration
    rabbitmq_url: str = Field(default="amqp://guest:guest@localhost:5672//")
    rabbitmq_queue_prefix: str = Field(default="hr_platform")

    # JWT Configuration
    jwt_secret: str = Field(default="your-super-secret-key-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiry_hours: int = Field(default=24)
    jwt_refresh_expiry_days: int = Field(default=30)

    # AWS S3 Configuration
    aws_s3_bucket: str = Field(default="hr-platform-bucket")
    aws_s3_region: str = Field(default="us-east-1")
    aws_access_key_id: Optional[str] = Field(default=None)
    aws_secret_access_key: Optional[str] = Field(default=None)

    # External APIs Configuration
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    sendgrid_api_key: Optional[str] = Field(default=None)

    # Email Configuration
    sendgrid_from_email: str = Field(default="noreply@hrplatform.com")
    sendgrid_from_name: str = Field(default="HR Platform")

    # Matching Configuration
    matching_skill_weight: float = Field(default=0.35)
    matching_experience_weight: float = Field(default=0.25)
    matching_education_weight: float = Field(default=0.15)
    matching_location_weight: float = Field(default=0.10)
    matching_rate_weight: float = Field(default=0.10)
    matching_availability_weight: float = Field(default=0.05)

    # CORS Configuration
    cors_origins: Any = Field(default="http://localhost:3000,http://localhost:8000")

    # Pagination Configuration
    default_page_size: int = Field(default=20)
    max_page_size: int = Field(default=100)

    # Feature Flags
    enable_ai_parsing: bool = Field(default=True)
    enable_auto_matching: bool = Field(default=True)
    enable_email_notifications: bool = Field(default=True)
    enable_supplier_distribution: bool = Field(default=True)

    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def matching_default_weights(self) -> Dict[str, float]:
        """Return matching weights as a dictionary."""
        return {
            "skill": self.matching_skill_weight,
            "experience": self.matching_experience_weight,
            "education": self.matching_education_weight,
            "location": self.matching_location_weight,
            "rate": self.matching_rate_weight,
            "availability": self.matching_availability_weight,
        }

    def validate_weights(self) -> bool:
        """Validate that matching weights sum to 1.0."""
        total = sum(self.matching_default_weights.values())
        return abs(total - 1.0) < 0.01


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
