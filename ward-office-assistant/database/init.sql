-- Placeholder init script, run automatically by the postgres Docker image
-- on first container start (mounted at /docker-entrypoint-initdb.d).
--
-- Prefer managing the actual schema through Alembic migrations
-- (backend/alembic/) once models stabilize. This file is only for things
-- that must exist before the app's first migration runs, e.g. extensions:

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- TODO: once Alembic is set up (`alembic init alembic` inside backend/),
-- remove manual table creation from here entirely and rely on
-- `alembic upgrade head` as part of deployment.
