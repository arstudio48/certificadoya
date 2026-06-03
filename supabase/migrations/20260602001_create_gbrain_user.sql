-- Create gbrain user for remote database access
-- This user will have limited privileges but enough for gbrain's vector store

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'gbrain') THEN
    CREATE ROLE gbrain WITH LOGIN PASSWORD 'gbr41n_supabase_rmt' NOBYPASSRLS;
  END IF;
END
$$;

-- Grant schema permissions
GRANT USAGE ON SCHEMA public TO gbrain;
GRANT CREATE ON SCHEMA public TO gbrain;
GRANT USAGE ON SCHEMA extensions TO gbrain;
GRANT CREATE ON SCHEMA extensions TO gbrain;

-- Grant table permissions for all existing tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO gbrain;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA extensions TO gbrain;

-- Grant future table permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO gbrain;
ALTER DEFAULT PRIVILEGES IN SCHEMA extensions GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO gbrain;

-- Grant sequence usage
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO gbrain;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA extensions TO gbrain;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO gbrain;
