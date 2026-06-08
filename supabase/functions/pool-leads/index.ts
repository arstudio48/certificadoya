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
      .select('id, nombre, email, provincia, verificado, activo, modelo_pago, saldo_creditos, comision_por_lead, premium_hasta')
      .eq('token', sessionToken)
      .eq('activo', true)
      .maybeSingle()

    if (tokenError || !tecnico) {
      return new Response(JSON.stringify({ error: 'Sesión no válida. Inicia sesión de nuevo.' }), { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    if (!tecnico.verificado) {
      return new Response(JSON.stringify({ error: 'Tu cuenta está pendiente de verificación. Te avisaremos cuando esté lista.' }), { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // Obtener provincias del técnico (capitalización original)
    const provincias = tecnico.provincia
      ? tecnico.provincia.split(',').map(p => p.trim())
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
        .select('id, nombre_cliente, provincia, codigo_postal, m2, tipo_inmueble, presupuesto_min, presupuesto_max, estado, created_at')
        .not('estado', 'eq', 'cancelado')

      // Si el técnico tiene provincias asignadas, filtrar por provincia
      if (provincias.length > 0) {
        // Usar OR con ilike para matching case-insensitive
        const filtros = provincias.map(p => `provincia.ilike.%${p}%`).join(',')
        query = query.or(filtros)
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

        // ============================================================
        // Verificar pago / suscripción antes de asignar
        // ============================================================
        let saldoRestante = tecnico.saldo_creditos ?? 0

        if (tecnico.modelo_pago === 'premium') {
          // Verificar suscripción premium activa
          if (!tecnico.premium_hasta || new Date(tecnico.premium_hasta) <= new Date()) {
            return new Response(JSON.stringify({
              error: 'Tu suscripción premium ha expirado. Renueva para seguir aceptando encargos.'
            }), { status: 402, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
          }
          // Premium: asignación gratuita, no descontar crédito
        } else {
          // Modelo por lead: descontar 1 crédito
          if (saldoRestante < 1) {
            return new Response(JSON.stringify({
              error: 'Saldo insuficiente. Debes recargar créditos para aceptar encargos.'
            }), { status: 402, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
          }

          // Débito atómico con condición saldo_creditos >= 1
          const { error: debitError, count: affectedRows } = await supabase
            .from('tecnicos')
            .update({ saldo_creditos: saldoRestante - 1 })
            .eq('id', tecnico.id)
            .gte('saldo_creditos', 1)

          if (debitError) {
            return new Response(JSON.stringify({ error: 'Error al procesar el pago. Intenta de nuevo.' }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
          }

          // Si affectedRows es 0, otro proceso agotó el saldo concurrentemente
          if (affectedRows === 0) {
            return new Response(JSON.stringify({
              error: 'Saldo insuficiente. Debes recargar créditos para aceptar encargos.'
            }), { status: 402, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
          }

          saldoRestante -= 1

          // Registrar transacción
          const leadIdShort = leadId.slice(0, 8)
          const { error: txError } = await supabase
            .from('transacciones_tecnicos')
            .insert({
              tecnico_id: tecnico.id,
              tipo: 'gasto_lead',
              cantidad: 1,
              concepto: 'Lead asignado: ' + leadIdShort
            })

          if (txError) {
            console.error('Error al registrar transacción:', txError.message)
            // No bloquear la asignación por un error de registro
          }
        }

        // ============================================================
        // Asignar lead
        // ============================================================
        const now = new Date().toISOString()
        await supabase
          .from('leads')
          .update({
            estado: 'asignado',
            tecnico_asignado: tecnico.id,
            fecha_asignacion: now
          })
          .eq('id', leadId)

        // Armar respuesta
        const responseData: Record<string, unknown> = {
          success: true,
          message: 'Encargo aceptado. Recibirás los datos del cliente para contactarlo.',
          leadId,
          saldo_restante: saldoRestante
        }

        if (saldoRestante === 1) {
          responseData.advertencia = 'Te queda 1 crédito. Recarga pronto para seguir aceptando encargos.'
        }

        return new Response(JSON.stringify(responseData), {
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
