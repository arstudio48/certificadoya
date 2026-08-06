-- Migración: tabla de prospectos de técnicos (captación)
CREATE TABLE IF NOT EXISTS prospectos_tecnicos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nombre TEXT,
    empresa TEXT,
    email TEXT,
    telefono TEXT,
    provincia TEXT NOT NULL,
    localidad TEXT,
    colegiado TEXT,
    titulacion TEXT,
    fuente TEXT,  -- de dónde se obtuvo (COAAT, web, etc.)
    contactado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    es_test BOOLEAN DEFAULT FALSE
);

-- RLS: solo el propietario (service role) puede gestionar
ALTER TABLE prospectos_tecnicos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role full access" ON prospectos_tecnicos
    FOR ALL USING (true) WITH CHECK (true);
