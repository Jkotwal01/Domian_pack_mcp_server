-- Database Initialization Script for Domain Pack Generator
-- This script creates all tables, indexes, and constraints

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom enum types
CREATE TYPE session_status AS ENUM ('active', 'closed');
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for email lookups
CREATE INDEX ix_users_email ON users(email);

-- ============================================================================
-- DOMAIN_CONFIGS TABLE
-- ============================================================================
CREATE TABLE domain_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    config_json JSONB NOT NULL,
    
    -- Cached counts for performance
    entity_count INTEGER NOT NULL DEFAULT 0,
    relationship_count INTEGER NOT NULL DEFAULT 0,
    extraction_pattern_count INTEGER NOT NULL DEFAULT 0,
    key_term_count INTEGER NOT NULL DEFAULT 0,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for domain_configs
CREATE INDEX ix_domain_configs_owner ON domain_configs(owner_user_id);
CREATE INDEX ix_domain_configs_json ON domain_configs USING GIN (config_json);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_domain_configs_updated_at 
    BEFORE UPDATE ON domain_configs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- CHAT_SESSIONS TABLE
-- ============================================================================
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    domain_config_id UUID NOT NULL REFERENCES domain_configs(id) ON DELETE CASCADE,
    status session_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for chat_sessions
CREATE INDEX ix_chat_sessions_user ON chat_sessions(user_id);
CREATE INDEX ix_chat_sessions_domain ON chat_sessions(domain_config_id);

-- Unique constraint: Only one active session per user+domain
CREATE UNIQUE INDEX uq_user_domain_active_session 
    ON chat_sessions (user_id, domain_config_id, status) 
    WHERE status = 'active';

-- ============================================================================
-- CHAT_MESSAGES TABLE
-- ============================================================================
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for efficient message retrieval
CREATE INDEX ix_chat_messages_session ON chat_messages(session_id, created_at);

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Uncomment the following lines to insert sample data for testing

-- -- Sample user (password is 'password123' hashed with bcrypt)
-- INSERT INTO users (email, password_hash) VALUES 
-- ('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6');

-- -- Sample domain config
-- INSERT INTO domain_configs (owner_user_id, name, description, version, config_json, entity_count, relationship_count, extraction_pattern_count, key_term_count)
-- SELECT 
--     id,
--     'Healthcare Domain',
--     'Domain configuration for healthcare entities and relationships',
--     '1.0.0',
--     '{
--         "name": "Healthcare Domain",
--         "description": "Domain configuration for healthcare entities and relationships",
--         "version": "1.0.0",
--         "entities": [
--             {
--                 "name": "Patient",
--                 "type": "PATIENT",
--                 "description": "A patient in the healthcare system",
--                 "attributes": [
--                     {"name": "name", "description": "Patient full name"},
--                     {"name": "age", "description": "Patient age"}
--                 ],
--                 "synonyms": ["Individual", "Person"]
--             },
--             {
--                 "name": "Doctor",
--                 "type": "DOCTOR",
--                 "description": "A medical doctor",
--                 "attributes": [
--                     {"name": "name", "description": "Doctor full name"},
--                     {"name": "specialization", "description": "Medical specialization"}
--                 ],
--                 "synonyms": ["Physician", "Medical Professional"]
--             }
--         ],
--         "relationships": [
--             {
--                 "name": "TREATED_BY",
--                 "from": "PATIENT",
--                 "to": "DOCTOR",
--                 "description": "Patient is treated by a doctor",
--                 "attributes": [
--                     {"name": "date", "description": "Treatment date"}
--                 ]
--             }
--         ],
--         "extraction_patterns": [
--             {
--                 "pattern": "\\bDr\\. [A-Z][a-z]+ [A-Z][a-z]+\\b",
--                 "entity_type": "DOCTOR",
--                 "attribute": "name",
--                 "extract_full_match": true,
--                 "confidence": 0.9
--             }
--         ],
--         "key_terms": ["patient", "doctor", "treatment", "diagnosis"]
--     }'::jsonb,
--     2,
--     1,
--     1,
--     4
-- FROM users WHERE email = 'test@example.com';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Run these queries to verify the database setup

-- Check all tables
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Check all indexes
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Check enum types
SELECT 
    n.nspname AS schema,
    t.typname AS type_name,
    e.enumlabel AS enum_value
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
WHERE n.nspname = 'public'
ORDER BY t.typname, e.enumsortorder;

-- ============================================================================
-- CLEANUP SCRIPT (Use with caution!)
-- ============================================================================

-- Uncomment to drop all tables and start fresh
-- WARNING: This will delete all data!

-- DROP TABLE IF EXISTS chat_messages CASCADE;
-- DROP TABLE IF EXISTS chat_sessions CASCADE;
-- DROP TABLE IF EXISTS domain_configs CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;
-- DROP TYPE IF EXISTS message_role;
-- DROP TYPE IF EXISTS session_status;
