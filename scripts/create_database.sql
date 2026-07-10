-- CareBridge-AI Database Setup Script
-- Run this with: psql -U postgres -f create_database.sql

-- Create database
CREATE DATABASE carebridge_db;

-- Connect to database
\c carebridge_db

-- Set timezone
ALTER DATABASE carebridge_db SET timezone TO 'Asia/Kolkata';

-- Verify
SELECT current_database(), version();
