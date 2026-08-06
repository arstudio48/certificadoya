-- Tabla de pisos para Nueva Era (portal inmobiliario)
create table if not exists public.pisos (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  -- Datos del anuncio
  titulo text not null,
  descripcion text,
  precio integer not null,
  tipo text not null default 'piso', -- piso, casa, adosado, atico, local, terreno
  operacion text not null default 'venta', -- venta, alquiler

  -- Ubicación
  provincia text not null,
  ciudad text,
  codigo_postal text,
  direccion text, -- solo calle, sin número exacto por privacidad

  -- Características
  m2 integer,
  m2_utiles integer,
  habitaciones integer default 0,
  banos integer default 0,
  planta text,
  ascensor boolean default false,
  garaje boolean default false,
  terraza boolean default false,
  piscina boolean default false,
  certificado_energetico text, -- A, B, C, D, E, F, G

  -- Precios adicionales
  precio_alquiler integer, -- si aplica

  -- Contacto
  nombre_contacto text,
  email_contacto text not null,
  telefono_contacto text,

  -- Multimedia
  fotos jsonb default '[]'::jsonb,

  -- Estado
  activo boolean not null default true,
  destacado boolean not null default false,
  visitas integer not null default 0
);

-- Índices
create index if not exists idx_pisos_provincia on public.pisos(provincia);
create index if not exists idx_pisos_activo on public.pisos(activo);
create index if not exists idx_pisos_operacion on public.pisos(operacion);
create index if not exists idx_pisos_precio on public.pisos(precio);
create index if not exists idx_pisos_created_at on public.pisos(created_at desc);

-- Trigger para updated_at
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_pisos_updated_at on public.pisos;
create trigger trg_pisos_updated_at
  before update on public.pisos
  for each row execute function public.handle_updated_at();

-- RLS
alter table public.pisos enable row level security;

-- Cualquiera puede leer pisos activos
create policy "Pisos activos visibles para todos"
  on public.pisos for select
  using (activo = true);

-- Los propietarios pueden ver sus propios pisos (incluyendo inactivos)
create policy "Propietarios pueden ver sus pisos"
  on public.pisos for select
  using (email_contacto = current_setting('request.jwt.claims', true)::json->>'email');

-- Cualquiera puede insertar (sin auth, como un formulario web)
create policy "Cualquiera puede publicar un piso"
  on public.pisos for insert
  with check (true);
