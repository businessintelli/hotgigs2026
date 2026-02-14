-- HotGigs 2026 - PostgreSQL Initialization Script
-- This runs automatically when the postgres container is first created

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create additional schemas if needed
-- CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE hotgigs_db TO hotgigs;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'HotGigs 2026 database initialized successfully';
END $$;
