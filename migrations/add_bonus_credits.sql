-- Migration: add bonus_credits column
-- Run in Supabase SQL Editor for existing databases

ALTER TABLE users ADD COLUMN IF NOT EXISTS bonus_credits INTEGER NOT NULL DEFAULT 0;
