import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  // Obtener token de sesión del header
  const authHeader = req.headers.get('authorization') || ''
  const sessionToken = authHeader.replace('Bearer ', '')

  if (!sessionToken) {
    return new Response(JSON.stringify({ error: 'Token de sesión requerido' }), { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }

  const supabase = createClient(supabaseUrl, supabaseKey)

  try {
    // Verificar token de sesión y obtener datos del técnico
    const { data: tecnico, error: tokenError } = await supabase
      .from('tecnicos')
      .select('id, nombre, email, provincia, verificado, activo')
      .eq('token', sessionToken)
      .eq('activo', true)
      .maybeSingle()

    if (tokenError || !tecnico) {
      return new Response(JSON.stringify({ error: 'Sesión no válida. Inicia sesión de nuevo.' }), { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    if (!tecnico.verificado) {
      return new Response(JSON.stringify({ error: 'Tu cuenta está pendiente de verificación. Te avisaremos cuando esté lista.' }), { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // Obtener provincias del técnico
    const provincias = tecnico.provincia
      ? tecnico.provincia.split(',').map(p => p.trim().toLowerCase())
      : []

    // Acepta GET (listar) y POST (aceptar/rechazar)
    if (req.method === 'GET') {
      // ============================================================
      // GET: Listar leads disponibles para el técnico
      // ============================================================
      const url = new URL(req.url)
      const estado = url.searchParams.get('estado') || 'pendiente'

      let query = supabase
        .from('leads')
        .select('id, nombre_cliente, zona, codigo_postal, m2, tipo_inmueble, presupuesto_min, presupuesto_max, estado, created_at')
        .not('estado', 'eq', 'cancelado')

      // Si el técnico tiene provincias asignadas, filtrar por zona
      if (provincias.length > 0) {
        query = query.in('zona', provincias)
      }

      // Si es un estado específico
      if (estado !== 'todos') {
        query = query.eq('estado', estado)
      }

      // Ordenar por fecha descendente (más recientes primero)
      query = query.order('created_at', { ascending: false }).limit(50)

      const { data: leads, error: leadsError } = await query

      if (leadsError) {
        return new Response(JSON.stringify({ error: leadsError.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      return new Response(JSON.stringify({
        success: true,
        tecnico: { nombre: tecnico.nombre, email: tecnico.email },
        leads
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    if (req.method === 'POST') {
      // ============================================================
      // POST: Aceptar lead
      // ============================================================
      const { action, leadId } = await req.json()

      if (!action || !leadId) {
        return new Response(JSON.stringify({ error: 'Faltan datos (action, leadId)' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      if (action === 'aceptar') {
        // Verificar que el lead sigue disponible
        const { data: lead, error: leadError } = await supabase
          .from('leads')
          .select('id, nombre_cliente, estado')
          .eq('id', leadId)
          .maybeSingle()

        if (leadError || !lead) {
          return new Response(JSON.stringify({ error: 'Lead no encontrado' }), { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
        }

        if (lead.estado !== 'pendiente') {
          return new Response(JSON.stringify({ error: 'Este encargo ya no está disponible (otro técnico lo aceptó)' }), { status: 409, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
        }

        // Actualizar lead
        await supabase
          .from('leads')
          .update({
            estado: 'asignado',
            tecnico_asignado: tecnico.id,
            updated_at: new Date().toISOString()
          })
          .eq('id', leadId)

        return new Response(JSON.stringify({
          success: true,
          message: 'Encargo aceptado. Recibirás los datos del cliente para contactarlo.',
          leadId
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      if (action === 'rechazar') {
        // Solo rechazar si está pendiente
        const { data: lead } = await supabase
          .from('leads')
          .select('id, estado')
          .eq('id', leadId)
          .maybeSingle()

        if (lead && lead.estado === 'pendiente') {
          // No cambiar estado, solo notificar que el técnico lo rechazó
          // Podríamos llevar un contador de rechazos, pero por ahora no hacemos nada
        }

        return new Response(JSON.stringify({
          success: true,
          message: 'Encargo rechazado. Seguirás recibiendo nuevas solicitudes.'
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      return new Response(JSON.stringify({ error: 'Acción no válida' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers: corsHeaders })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
