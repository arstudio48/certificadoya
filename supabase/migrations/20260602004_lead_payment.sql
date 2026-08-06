-- =============================================================================
-- Migration: Lead-based payment system for técnicos
-- Description: Adds support for pay-per-lead and premium subscription models
-- for técnicos in CertificadoYa. Includes credit system, Stripe integration,
-- and transaction history.
--
-- Safe for repeated execution (uses IF NOT EXISTS / ADD COLUMN IF NOT EXISTS).
-- =============================================================================
-- Date: 2026-06-02
-- =============================================================================

-- =============================================================================
-- 1. New columns in tecnicos — payment model & Stripe fields
-- =============================================================================
ALTER TABLE tecnicos
  ADD COLUMN IF NOT EXISTS modelo_pago          TEXT        DEFAULT 'lead',
  ADD COLUMN IF NOT EXISTS comision_por_lead    NUMERIC(6,2) DEFAULT 4.00,
  ADD COLUMN IF NOT EXISTS saldo_creditos       INTEGER     DEFAULT 0,
  ADD COLUMN IF NOT EXISTS stripe_customer_id   TEXT,
  ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT,
  ADD COLUMN IF NOT EXISTS premium_hasta        TIMESTAMPTZ;

-- Add CHECK constraint for modelo_pago (safe: only if it doesn't already exist)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM   pg_constraint
    WHERE  conrelid = 'tecnicos'::regclass
      AND  conname  = 'tecnicos_modelo_pago_check'
  ) THEN
    ALTER TABLE tecnicos
      ADD CONSTRAINT tecnicos_modelo_pago_check
        CHECK (modelo_pago IN ('lead', 'premium'));
  END IF;
END $$;

-- =============================================================================
-- 2. New table: transacciones_tecnicos — credit purchases & expenses
-- =============================================================================
CREATE TABLE IF NOT EXISTS transacciones_tecnicos (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tecnico_id          UUID        NOT NULL REFERENCES tecnicos(id) ON DELETE CASCADE,
  tipo                TEXT        NOT NULL,
  cantidad            INTEGER     NOT NULL DEFAULT 0,
  importe_eur         NUMERIC(8,2),
  concepto            TEXT,
  stripe_payment_intent TEXT,
  stripe_session_id   TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT transacciones_tecnicos_tipo_check
    CHECK (tipo IN ('compra_creditos','gasto_lead','suscripcion_premium','admin_ajuste'))
);

-- =============================================================================
-- 3. New columns in leads — payment intent & technician assignment
-- =============================================================================
ALTER TABLE leads
  ADD COLUMN IF NOT EXISTS stripe_payment_intent TEXT,
  ADD COLUMN IF NOT EXISTS presupuesto_id        UUID REFERENCES presupuestos(id),
  ADD COLUMN IF NOT EXISTS fecha_asignacion      TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS ultimo_aviso_saldo    TIMESTAMPTZ;

-- =============================================================================
-- 4. New columns in presupuestos — Stripe payment tracking
-- =============================================================================
ALTER TABLE presupuestos
  ADD COLUMN IF NOT EXISTS stripe_payment_intent TEXT,
  ADD COLUMN IF NOT EXISTS stripe_session_id     TEXT,
  ADD COLUMN IF NOT EXISTS fecha_pago            TIMESTAMPTZ;

-- =============================================================================
-- 5. Indexes for performance
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_transacciones_tecnico
  ON transacciones_tecnicos (tecnico_id);

CREATE INDEX IF NOT EXISTS idx_transacciones_fecha
  ON transacciones_tecnicos (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_tecnicos_modelo
  ON tecnicos (modelo_pago);
