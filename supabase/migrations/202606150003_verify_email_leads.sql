-- Añadir columnas para verificación de email en leads
ALTER TABLE leads ADD COLUMN IF NOT EXISTS email_verificado BOOLEAN DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS token_verificacion TEXT DEFAULT null;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS email_verificado_en TIMESTAMPTZ DEFAULT null;
COMMENT ON COLUMN leads.email_verificado IS 'False hasta que el usuario confirme su email via link';
COMMENT ON COLUMN leads.token_verificacion IS 'Token único enviado por email para verificación';
COMMENT ON COLUMN leads.email_verificado_en IS 'Timestamp de cuando se verificó el email';
