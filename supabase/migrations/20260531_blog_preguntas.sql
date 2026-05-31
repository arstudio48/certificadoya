CREATE TABLE IF NOT EXISTS blog_preguntas (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  articulo_slug text NOT NULL,
  user_email text NOT NULL,
  user_name text NOT NULL DEFAULT '',
  pregunta text NOT NULL,
  respuesta text DEFAULT '',
  visible boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_blog_preguntas_slug ON blog_preguntas (articulo_slug);
CREATE INDEX IF NOT EXISTS idx_blog_preguntas_visible ON blog_preguntas (visible);
CREATE TABLE IF NOT EXISTS blog_lectores (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  nombre text DEFAULT '',
  token text DEFAULT '',
  token_expira timestamptz DEFAULT now(),
  ultimo_acceso timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now()
);
