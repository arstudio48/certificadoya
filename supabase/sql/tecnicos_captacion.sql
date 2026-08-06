-- Tabla para captación de técnicos vía landing /hazte-certificador/
-- Ejecutar en el SQL Editor de Supabase (proyecto certificadoya)

create table if not exists public.tecnicos_captacion (
  id uuid primary key default gen_random_uuid(),
  nombre text not null,
  email text not null unique,
  telefono text not null,
  provincia text not null,
  titulacion text not null,
  modulos_rd659 text,
  mensaje text,
  origen text,
  token_confirmacion text unique,
  confirmado boolean not null default false,
  confirmado_en timestamptz,
  contactado boolean not null default false,
  notas_internas text,
  creado_en timestamptz not null default now()
);

create index if not exists idx_tec_confirmado on public.tecnicos_captacion(confirmado);
create index if not exists idx_tec_provincia on public.tecnicos_captacion(provincia);
create index if not exists idx_tec_creado on public.tecnicos_captacion(creado_en desc);

-- RLS: nadie puede leer/escribir excepto la service_role (que usan las Edge Functions).
alter table public.tecnicos_captacion enable row level security;
