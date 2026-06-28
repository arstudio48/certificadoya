-- Tabla de mensajes entre técnico y cliente
create table if not exists public.mensajes_encargo (
  id uuid default gen_random_uuid() primary key,
  encargo_id uuid not null references public.leads(id) on delete cascade,
  de_tecnico boolean not null default true, -- true = técnico, false = cliente
  mensaje text not null,
  leido boolean not null default false,
  created_at timestamptz default now()
);

-- Índices
create index if not exists idx_mensajes_encargo_id on public.mensajes_encargo(encargo_id);
create index if not exists idx_mensajes_created_at on public.mensajes_encargo(created_at);

-- RLS: solo lectura/escritura via Edge Function (service_role)
alter table public.mensajes_encargo enable row level security;
