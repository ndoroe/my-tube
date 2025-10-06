-- MyTube Database Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance (will be created by SQLAlchemy migrations)
-- These are just placeholders for future optimizations

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE mytube TO mytube_user;

-- Set timezone
SET timezone = 'UTC';
