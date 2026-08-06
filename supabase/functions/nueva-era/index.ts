import { serve } from 'https://deno.land/std@0.177.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;

const supabase = createClient(supabaseUrl, supabaseKey);

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders });

  const url = new URL(req.url);
  const action = url.searchParams.get('action') || 'listar';

  try {
    switch (action) {
      case 'listar':
        return await listarPisos(url);
      case 'buscar':
        return await buscarPisos(url);
      case 'detalle':
        return await detallePiso(url);
      case 'publicar':
        return await publicarPiso(req);
      default:
        return json({ error: 'Acción no válida' }, 400);
    }
  } catch (err) {
    return json({ error: err.message }, 500);
  }
});

async function listarPisos(url: URL) {
  const page = parseInt(url.searchParams.get('page') || '1');
  const limit = 20;
  const offset = (page - 1) * limit;
  const provincia = url.searchParams.get('provincia');
  const operacion = url.searchParams.get('operacion') || 'venta';
  const tipo = url.searchParams.get('tipo');
  const precioMin = url.searchParams.get('precio_min');
  const precioMax = url.searchParams.get('precio_max');

  let query = supabase
    .from('pisos')
    .select('*', { count: 'exact' })
    .eq('activo', true)
    .eq('operacion', operacion)
    .order('destacado', { ascending: false })
    .order('created_at', { ascending: false })
    .range(offset, offset + limit - 1);

  if (provincia) query = query.eq('provincia', provincia);
  if (tipo) query = query.eq('tipo', tipo);
  if (precioMin) query = query.gte('precio', parseInt(precioMin));
  if (precioMax) query = query.lte('precio', parseInt(precioMax));

  const { data, error, count } = await query;
  if (error) return json({ error: error.message }, 500);

  return json({
    pisos: data,
    total: count,
    page,
    totalPages: Math.ceil((count || 0) / limit),
  });
}

async function buscarPisos(url: URL) {
  const q = url.searchParams.get('q') || '';
  const provincia = url.searchParams.get('provincia');
  const operacion = url.searchParams.get('operacion') || 'venta';

  let query = supabase
    .from('pisos')
    .select('id, titulo, precio, provincia, ciudad, tipo, m2, habitaciones, fotos, created_at, operacion')
    .eq('activo', true)
    .eq('operacion', operacion)
    .order('created_at', { ascending: false })
    .limit(30);

  if (provincia) query = query.eq('provincia', provincia);
  if (q) {
    query = query.or(`titulo.ilike.%${q}%,ciudad.ilike.%${q}%,descripcion.ilike.%${q}%`);
  }

  const { data, error } = await query;
  if (error) return json({ error: error.message }, 500);
  return json({ pisos: data });
}

async function detallePiso(url: URL) {
  const id = url.searchParams.get('id');
  if (!id) return json({ error: 'Falta id del piso' }, 400);

  const { data, error } = await supabase
    .from('pisos')
    .select('*')
    .eq('id', id)
    .single();

  if (error) return json({ error: 'Piso no encontrado' }, 404);

  // Incrementar visitas
  await supabase.rpc('incrementar_visita', { piso_id: id });

  return json({ piso: data });
}

async function publicarPiso(req: Request) {
  const body = await req.json();

  const { data, error } = await supabase
    .from('pisos')
    .insert({
      titulo: body.titulo,
      descripcion: body.descripcion,
      precio: body.precio,
      tipo: body.tipo || 'piso',
      operacion: body.operacion || 'venta',
      provincia: body.provincia,
      ciudad: body.ciudad,
      codigo_postal: body.codigo_postal,
      m2: body.m2,
      habitaciones: body.habitaciones || 0,
      banos: body.banos || 0,
      nombre_contacto: body.nombre_contacto,
      email_contacto: body.email_contacto,
      telefono_contacto: body.telefono_contacto,
      fotos: body.fotos || [],
      certificado_energetico: body.certificado_energetico,
      garaje: body.garaje || false,
      terraza: body.terraza || false,
      ascensor: body.ascensor || false,
      planta: body.planta,
    })
    .select('id')
    .single();

  if (error) {
    return json({ error: error.message }, 500);
  }

  return json({
    success: true,
    id: data.id,
    url: `https://arstudio48.github.io/nueva-era/piso.html?id=${data.id}`,
  });
}

function json(data: any, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  });
}
