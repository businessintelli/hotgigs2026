"""Tests for Settings configuration."""
import pytest

from config.settings import Settings


class TestSettings:
    """Test suite for Settings."""

    @pytest.mark.unit
    def test_settings_initialization(self):
        """Test settings initialization."""
        settings = Settings(
            debug=True,
            app_name="Test HR Platform",
        )

        assert settings.debug is True
        assert settings.app_name == "Test HR Platform"

    @pytest.mark.unit
    def test_settings_defaults(self):
        """Test settings default values."""
        settings = Settings()

        assert settings.app_name == "HR Automation Platform"
        assert settings.debug is False
        assert settings.log_level == "INFO"

    @pytest.mark.unit
    def test_settings_database_config(self):
        """Test database configuration."""
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost/db"
        )

        assert "postgresql" in settings.database_url

    @pytest.mark.unit
    def test_settings_jwt_config(self):
        """Test JWT configuration."""
        settings = Settings(
            jwt_secret="test-secret",
            jwt_algorithm="HS256",
            jwt_expiry_hours=24,
        )

        assert settings.jwt_secret == "test-secret"
        assert settings.jwt_algorithm == "HS256"
        assert settings.jwt_expiry_hours == 24

    @pytest.mark.unit
    def test_settings_matching_weights(self):
        """Test matching weights configuration."""
        settings = Settings()

        weights = settings.matching_default_weights
        assert "skill" in weights
        assert "experience" in weights
        assert "education" in weights

    @pytest.mark.unit
    def test_settings_weight_validation(self):
        """Test matching weights sum to 1.0."""
        settings = Settings()

        assert settings.validate_weights() is True

    @pytest.mark.unit
    def test_settings_cors_origins_parsing(self):
        """Test CORS origins parsing."""
        settings = Settings(
            cors_origins="http://localhost:3000,http://localhost:8000"
        )

        assert isinstance(settings.cors_origins, list)
        assert len(settings.cors_origins) == 2
        assert "http://localhost:3000" in settings.cors_origins

    @pytest.mark.unit
    def test_settings_feature_flags(self):
        """Test feature flags."""
        settings = Settings(
            enable_ai_parsing=False,
            enable_auto_matching=False,
            enable_email_notifications=False,
        )

        assert settings.enable_ai_parsing is False
        assert settings.enable_auto_matching is False
        assert settings.enable_email_notifications is False

    @pytest.mark.unit
    def test_settings_aws_config(self):
        """Test AWS configuration."""
        settings = Settings(
            aws_s3_bucket="test-bucket",
            aws_s3_region="us-west-2",
        )

        assert settings.aws_s3_bucket == "test-bucket"
        assert settings.aws_s3_region == "us-west-2"

    @pytest.mark.unit
    def test_settings_pagination(self):
        """Test pagination configuration."""
        settings = Settings(
            default_page_size=50,
            max_page_size=200,
        )

        assert settings.default_page_size == 50
        assert settings.max_page_size == 200

    @pytest.mark.unit
    def test_settings_email_config(self):
        """Test email configuration."""
        settings = Settings(
            sendgrid_from_email="noreply@test.com",
            sendgrid_from_name="Test HR Platform",
        )

        assert settings.sendgrid_from_email == "noreply@test.com"
        assert settings.sendgrid_from_name == "Test HR Platform"

    @pytest.mark.unit
    def test_settings_redis_config(self):
        """Test Redis configuration."""
        settings = Settings(
            redis_url="redis://localhost:6379/1"
        )

        assert "redis" in settings.redis_url

    @pytest.mark.unit
    def test_settings_rabbitmq_config(self):
        """Test RabbitMQ configuration."""
        settings = Settings(
            rabbitmq_url="amqp://guest:guest@localhost:5672//",
            rabbitmq_queue_prefix="test_",
        )

        assert "amqp" in settings.rabbitmq_url
        assert settings.rabbitmq_queue_prefix == "test_"

    @pytest.mark.unit
    def test_settings_matching_weights_customization(self):
        """Test custom matching weights."""
        settings = Settings(
            matching_skill_weight=0.40,
            matching_experience_weight=0.30,
            matching_education_weight=0.10,
            matching_location_weight=0.10,
            matching_rate_weight=0.05,
            matching_availability_weight=0.05,
        )

        weights = settings.matching_default_weights
        assert weights["skill"] == 0.40
        assert weights["experience"] == 0.30
        assert settings.validate_weights() is True

    @pytest.mark.unit
    def test_settings_database_pool_config(self):
        """Test database pool configuration."""
        settings = Settings(
            database_pool_size=30,
            database_max_overflow=15,
            database_pool_recycle=7200,
        )

        assert settings.database_pool_size == 30
        assert settings.database_max_overflow == 15
        assert settings.database_pool_recycle == 7200
