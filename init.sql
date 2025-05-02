CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA logs;

CREATE TYPE status_type AS ENUM ('STANDBY', 'IN-PROCESS', 'FAILED', 'DONE');
CREATE TYPE role_type AS ENUM ('ADMIN', 'DEFAULT');
CREATE TYPE arrange_type AS ENUM ('DETAILS', 'PATIENTS', 'METRICS');

CREATE TABLE IF NOT EXISTS docs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    status status_type NOT NULL DEFAULT 'STANDBY',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS params (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    synonyms TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role role_type NOT NULL DEFAULT 'DEFAULT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS arranges (
    doc_id UUID REFERENCES docs(id) ON DELETE CASCADE,
    output JSONB,
    status status_type NOT NULL DEFAULT 'STANDBY',
    type arrange_type NOT NULL,
    duration NUMERIC(25),
    updated_at TIMESTAMP,
    CONSTRAINT unique_doc_type UNIQUE (doc_id, type)
);
CREATE TABLE IF NOT EXISTS logs.arranges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_id UUID REFERENCES docs(id) ON DELETE CASCADE,
    output JSONB,
    type arrange_type NOT NULL,
    duration NUMERIC(25),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);