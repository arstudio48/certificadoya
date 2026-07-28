-- Make codigo_postal nullable for calculator leads
ALTER TABLE leads ALTER COLUMN codigo_postal DROP NOT NULL;
