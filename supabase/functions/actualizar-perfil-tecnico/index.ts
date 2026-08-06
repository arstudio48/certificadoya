import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

function normalizarLista(v: unknown): string[] {
  if (!v) return []
  if (Array.isArray(v)) return v.map((x) => String(x).trim()).filter(Boolean)
  return String(v).split(',').map((x) => x.trim()).filter(Boolean)
}

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })

  // ── Auth: token de sesión (Bearer) ──
  const authHeader = req.headers.get('authorization') || ''
  const sessionToken = authHeader.replace('Bearer ', '')
  if (!sessionToken) {
    return new Response(JSON.stringify({ error: 'Token de sesión requerido' }), { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }

  const supabase = createClient(supabaseUrl, supabaseKey)

  try {
    const { data: tecnico, error: tokenError } = await supabase
      .from('tecnicos')
      .select('id, nombre, apellidos, email, telefono, titulacion, numero_colegiado, provincia, cp_cobertura, zonas_cobertura, biografia, precio_m2, iban, tipo_cobro, plan, activo, verificado')
      .eq('token', sessionToken)
      .eq('activo', true)
      .maybeSingle()

    if (tokenError || !tecnico) {
      return new Response(JSON.stringify({ error: 'Sesión no válida. Inicia sesión de nuevo.' }), { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // ============================================================
    // GET: devolver perfil actual
    // ============================================================
    if (req.method === 'GET') {
      const zonas = tecnico.zonas_cobertura || {}
      return new Response(JSON.stringify({
        success: true,
        tecnico: {
          id: tecnico.id,
          nombre: tecnico.nombre,
          apellidos: tecnico.apellidos,
          email: tecnico.email,
          telefono: tecnico.telefono,
          titulacion: tecnico.titulacion,
          numero_colegiado: tecnico.numero_colegiado,
          provincia: tecnico.provincia || '',
          cp_cobertura: tecnico.cp_cobertura || '',
          biografia: tecnico.biografia || '',
          precio_m2: tecnico.precio_m2,
          iban: tecnico.iban || '',
          tipo_cobro: tecnico.tipo_cobro || 'directo',
          plan: tecnico.plan || 'por-lead',
          verificado: tecnico.verificado,
          zonas: {
            ccaa: zonas.ccaa || [],
            provincias: zonas.provincias || [],
            ciudades: zonas.ciudades || [],
            pueblos: zonas.pueblos || [],
            cps: zonas.cps || [],
          },
        },
      }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // ============================================================
    // POST: actualizar perfil + zonas
    // ============================================================
    if (req.method === 'POST') {
      const body = await req.json()

      const ccaa = normalizarLista(body.ccaa)
      const provincias = normalizarLista(body.provincias)
      const ciudades = normalizarLista(body.ciudades)
      const pueblos = normalizarLista(body.pueblos)
      const cps = normalizarLista(body.cps)

      // Construir update solo con campos presentes
      const update: Record<string, unknown> = { updated_at: new Date().toISOString() }

      if (body.nombre !== undefined) update.nombre = String(body.nombre).trim()
      if (body.apellidos !== undefined) update.apellidos = body.apellidos ? String(body.apellidos).trim() : null
      if (body.telefono !== undefined) update.telefono = String(body.telefono).trim()
      if (body.titulacion !== undefined) update.titulacion = body.titulacion ? String(body.titulacion).trim() : null
      if (body.numero_colegiado !== undefined) update.numero_colegiado = body.numero_colegiado ? String(body.numero_colegiado).trim() : null
      if (body.biografia !== undefined) update.biografia = body.biografia ? String(body.biografia).trim() : null
      if (body.precio_m2 !== undefined) update.precio_m2 = body.precio_m2 ? Number(body.precio_m2) : null
      if (body.iban !== undefined) update.iban = body.iban ? String(body.iban).trim() : null
      if (body.tipo_cobro !== undefined) update.tipo_cobro = String(body.tipo_cobro).trim()

      // Zonas: sincronizar columna legada provincia + nueva zonas_cobertura
      const tieneAlgo = ccaa.length > 0 || provincias.length > 0 || ciudades.length > 0 || pueblos.length > 0 || cps.length > 0
      if (tieneAlgo) {
        update.zonas_cobertura = { ccaa, provincias, ciudades, pueblos, cps }
        // Compatibilidad: provincia sigue siendo texto separado por comas (para pool-leads)
        if (provincias.length > 0) update.provincia = provincias.join(',')
        else if (ccaa.length > 0) update.provincia = ccaa.join(',') // fallback: el filtro ilike matchea
        update.cp_cobertura = cps.join(', ') || null
      }

      const { error: updateError } = await supabase
        .from('tecnicos')
        .update(update)
        .eq('id', tecnico.id)

      if (updateError) throw updateError

      return new Response(JSON.stringify({
        success: true,
        message: 'Perfil actualizado correctamente.',
        zonas: { ccaa, provincias, ciudades, pueblos, cps },
      }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers: corsHeaders })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
