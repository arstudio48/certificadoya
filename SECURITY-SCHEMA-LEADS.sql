-- SCHEMA SEGURO: Sistema de asignación de leads a prueba de fraude
-- CertificadoYa — 28 julio 2026

-- ============================================================================
-- ACTUALIZAR TABLA: leads (agregar campos de seguridad)
-- ============================================================================

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  payment_status text DEFAULT 'held' CHECK (payment_status IN ('held', 'released', 'refunded', 'disputed'));

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  token_asignacion uuid UNIQUE;

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  token_expira_en timestamp;

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  hito_visita_confirmada boolean DEFAULT false;

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  hito_ce3x_generado boolean DEFAULT false;

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  hito_registro_ccaa boolean DEFAULT false;

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  entrega_confirmada boolean DEFAULT false;

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  cliente_confirmo_recepcion boolean DEFAULT false;

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  timestamp_cliente_confirmacion timestamp;

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  comprobante_registro_ccaa jsonb;  -- {url, ocr_result, validado}

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  pdf_entregado_url text;

ALTER TABLE leads ADD COLUMN IF NOT EXISTS
  tecnico_id uuid REFERENCES tecnicos(id) ON DELETE RESTRICT;

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_leads_payment_status ON leads(payment_status);
CREATE INDEX IF NOT EXISTS idx_leads_token_asignacion ON leads(token_asignacion);
CREATE INDEX IF NOT EXISTS idx_leads_estado_tecnico ON leads(estado, tecnico_id);

-- ============================================================================
-- CREAR TABLA: lead_audit (auditoría completa de cada lead)
-- ============================================================================

CREATE TABLE IF NOT EXISTS lead_audit (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  accion text NOT NULL CHECK (accion IN 
    ('creado', 'asignado', 'aceptado', 'rechazado', 'abandonado', 
     'hito_visita', 'hito_ce3x', 'hito_registro', 'entrega_pendiente',
     'entrega_confirmada', 'completado', 'reembolsado', 'disputado')),
  usuario_id uuid,  -- técnico o admin
  usuario_tipo text CHECK (usuario_tipo IN ('tecnico', 'admin', 'cliente')),
  timestamp timestamp DEFAULT now(),
  ip_address text,
  geolocation jsonb,  -- {latitude, longitude, ciudad, pais}
  dispositivo_info jsonb,  -- {user_agent, browser, os}
  detalles jsonb,  -- metadata adicional según acción
  
  FOREIGN KEY (usuario_id) REFERENCES tecnicos(id) ON DELETE SET NULL,
  
  created_at timestamp DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_lead_id ON lead_audit(lead_id);
CREATE INDEX IF NOT EXISTS idx_audit_accion ON lead_audit(accion);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON lead_audit(timestamp DESC);

-- ============================================================================
-- CREAR TABLA: payment_audit (auditoría de pagos)
-- ============================================================================

CREATE TABLE IF NOT EXISTS payment_audit (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  stripe_payment_id text NOT NULL,
  stripe_charge_id text,  -- cargo real
  accion text NOT NULL CHECK (accion IN ('held', 'released', 'refunded', 'disputed', 'error')),
  monto numeric(10, 2) NOT NULL,
  comision_plataforma numeric(10, 2),  -- 18% de monto
  tasa_ccaa numeric(10, 2),  -- tasa autonómica
  monto_tecnico numeric(10, 2),  -- lo que recibe técnico
  timestamp timestamp DEFAULT now(),
  motivo text,  -- explicación si hay error/reembolso
  procesado_por text CHECK (procesado_por IN ('webhook', 'manual', 'sistema')),
  
  created_at timestamp DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_payment_lead_id ON payment_audit(lead_id);
CREATE INDEX IF NOT EXISTS idx_payment_stripe_id ON payment_audit(stripe_payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_accion ON payment_audit(accion);

-- ============================================================================
-- ACTUALIZAR TABLA: tecnicos (estadísticas y control)
-- ============================================================================

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  leads_asignados int DEFAULT 0;

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  leads_aceptados int DEFAULT 0;

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  leads_completados int DEFAULT 0;

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  leads_abandonados int DEFAULT 0;

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  tasa_abandono numeric(5, 2) DEFAULT 0;  -- porcentaje

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  reembolsos_recibidos int DEFAULT 0;

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  suspension_activa boolean DEFAULT false;

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  suspension_razon text;

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  suspension_hasta timestamp;

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  cuenta_bancaria_verificada boolean DEFAULT false;

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  cuenta_bancaria_iban text;  -- encriptado

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS
  stripe_connect_id text;  -- para pagos directos

-- ============================================================================
-- CREAR TABLA: lead_token (mapeo tokens no reutilizables)
-- ============================================================================

CREATE TABLE IF NOT EXISTS lead_token (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  tecnico_id uuid NOT NULL REFERENCES tecnicos(id) ON DELETE CASCADE,
  token text NOT NULL UNIQUE,
  tipo text CHECK (tipo IN ('asignacion', 'confirmacion_cliente', 'reset')),
  usado boolean DEFAULT false,
  usado_en timestamp,
  expira_en timestamp NOT NULL,
  ip_creado text,
  ip_usado text,
  
  created_at timestamp DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_token_lead_id ON lead_token(lead_id);
CREATE INDEX IF NOT EXISTS idx_token_tecnico_id ON lead_token(tecnico_id);
CREATE INDEX IF NOT EXISTS idx_token_string ON lead_token(token);
CREATE INDEX IF NOT EXISTS idx_token_expira ON lead_token(expira_en);

-- ============================================================================
-- CREAR TABLA: lead_disputa (manejo de conflictos)
-- ============================================================================

CREATE TABLE IF NOT EXISTS lead_disputa (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid NOT NULL UNIQUE REFERENCES leads(id) ON DELETE CASCADE,
  reportado_por text CHECK (reportado_por IN ('cliente', 'tecnico', 'sistema')),
  motivo text NOT NULL,
  descripcion text,
  estado text DEFAULT 'abierto' CHECK (estado IN ('abierto', 'investigacion', 'resuelto', 'cancelado')),
  resolucion text,  -- 'reembolso', 'completar_trabajo', 'ambas_partes', etc.
  monto_reembolso numeric(10, 2),
  admin_id uuid REFERENCES tecnicos(id),  -- admin que resuelve
  timestamp_reporte timestamp DEFAULT now(),
  timestamp_resolucion timestamp,
  
  created_at timestamp DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_disputa_estado ON lead_disputa(estado);
CREATE INDEX IF NOT EXISTS idx_disputa_timestamp ON lead_disputa(timestamp_reporte DESC);

-- ============================================================================
-- POLÍTICAS DE SEGURIDAD (Row Level Security - RLS)
-- ============================================================================

-- Los técnicos solo ven leads asignados a ellos
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

CREATE POLICY lead_tech_access ON leads
  FOR SELECT
  USING (
    -- Admin ve todo
    auth.role() = 'admin'
    OR
    -- Técnico ve solo leads asignados a él
    (tecnico_id = auth.uid())
    OR
    -- Cliente ve su propio lead (por email)
    (email_cliente = auth.email())
  );

-- Los técnicos no pueden modificar arbitrariamente
CREATE POLICY lead_tech_update ON leads
  FOR UPDATE
  USING (
    tecnico_id = auth.uid()
  )
  WITH CHECK (
    -- Solo pueden cambiar campos específicos
    tecnico_id = auth.uid()
  );

-- Auditoría: no se puede borrar/modificar audit logs
ALTER TABLE lead_audit ENABLE ROW LEVEL SECURITY;

CREATE POLICY audit_append_only ON lead_audit
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY audit_no_delete ON lead_audit
  FOR DELETE
  USING (false);  -- imposible borrar

-- ============================================================================
-- FUNCIONES TRIGGER (automáticas)
-- ============================================================================

-- Trigger 1: Actualizar tasa_abandono técnico
CREATE OR REPLACE FUNCTION actualizar_stats_tecnico()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.estado = 'abandonado' THEN
    UPDATE tecnicos
    SET 
      leads_abandonados = leads_abandonados + 1,
      tasa_abandono = (leads_abandonados + 1)::numeric / 
                      NULLIF(leads_asignados, 0) * 100
    WHERE id = NEW.tecnico_id;
  END IF;
  
  IF NEW.estado = 'completado' AND OLD.estado != 'completado' THEN
    UPDATE tecnicos
    SET leads_completados = leads_completados + 1
    WHERE id = NEW.tecnico_id;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_stats
AFTER UPDATE ON leads
FOR EACH ROW
EXECUTE FUNCTION actualizar_stats_tecnico();

-- Trigger 2: Log automático en auditoría
CREATE OR REPLACE FUNCTION log_lead_change()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO lead_audit (lead_id, accion, usuario_id, usuario_tipo, detalles)
  VALUES (
    NEW.id,
    CASE
      WHEN OLD IS NULL THEN 'creado'
      WHEN NEW.estado != OLD.estado THEN 'estado_' || NEW.estado
      ELSE 'actualizado'
    END,
    auth.uid(),
    'sistema',
    jsonb_build_object(
      'estado_anterior', OLD.estado,
      'estado_nuevo', NEW.estado,
      'timestamp', now()
    )
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_changes
AFTER UPDATE ON leads
FOR EACH ROW
EXECUTE FUNCTION log_lead_change();

-- ============================================================================
-- VISTAS (para reportes)
-- ============================================================================

CREATE OR REPLACE VIEW vista_leads_activos AS
SELECT
  l.id,
  l.nombre_cliente,
  l.email_cliente,
  l.provincia,
  l.estado,
  l.payment_status,
  l.tecnico_id,
  t.nombre as tecnico_nombre,
  l.created_at,
  EXTRACT(DAY FROM NOW() - l.created_at) as dias_asignado,
  l.hito_visita_confirmada,
  l.hito_ce3x_generado,
  l.hito_registro_ccaa,
  l.cliente_confirmo_recepcion
FROM leads l
LEFT JOIN tecnicos t ON l.tecnico_id = t.id
WHERE l.estado NOT IN ('completado', 'cancelado', 'abandonado');

CREATE OR REPLACE VIEW vista_leads_completados AS
SELECT
  l.id,
  l.nombre_cliente,
  l.provincia,
  l.tecnico_id,
  t.nombre as tecnico_nombre,
  l.created_at,
  l.timestamp_cliente_confirmacion,
  EXTRACT(DAY FROM l.timestamp_cliente_confirmacion - l.created_at) as dias_completacion,
  pa.monto,
  pa.monto_tecnico,
  pa.comision_plataforma,
  pa.timestamp as pago_fecha
FROM leads l
LEFT JOIN tecnicos t ON l.tecnico_id = t.id
LEFT JOIN payment_audit pa ON l.id = pa.lead_id AND pa.accion = 'released'
WHERE l.estado = 'completado';

CREATE OR REPLACE VIEW vista_fraude_potencial AS
SELECT
  l.id,
  l.nombre_cliente,
  l.tecnico_id,
  t.nombre as tecnico_nombre,
  l.estado,
  COUNT(DISTINCT la.id) as cambios_de_estado,
  MAX(la.timestamp) as ultimo_cambio,
  CASE
    WHEN l.leads_abandonados / NULLIF(l.leads_asignados, 0) > 0.2 THEN 'ALTO'
    WHEN l.leads_abandonados / NULLIF(l.leads_asignados, 0) > 0.1 THEN 'MEDIO'
    ELSE 'BAJO'
  END as riesgo_fraude,
  ld.estado as disputa_estado
FROM leads l
LEFT JOIN tecnicos t ON l.tecnico_id = t.id
LEFT JOIN lead_audit la ON l.id = la.lead_id
LEFT JOIN lead_disputa ld ON l.id = ld.lead_id
GROUP BY l.id, t.id, ld.id
HAVING COUNT(DISTINCT la.id) > 5  -- muchos cambios = sospechoso
   OR ld.estado = 'abierto';  -- o hay disputa activa

-- ============================================================================
-- ÍNDICES FINALES (performance)
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_leads_estado ON leads(estado);
CREATE INDEX IF NOT EXISTS idx_leads_payment_tecnico ON leads(payment_status, tecnico_id);
CREATE INDEX IF NOT EXISTS idx_leads_cliente ON leads(email_cliente, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tecnicos_suspension ON tecnicos(suspension_activa);
