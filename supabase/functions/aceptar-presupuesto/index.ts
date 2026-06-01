// Edge Function: aceptar-presupuesto
// Cliente verifica y paga el presupuesto vía Stripe
// Deploy: supabase functions deploy aceptar-presupuesto --no-verify-jwt
// Secrets needed: STRIPE_SECRET_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import Stripe from 'https://esm.sh/stripe@13.10.0?target=deno'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.0?target=deno'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY') || '', {
  apiVersion: '2023-10-16',
  httpClient: Stripe.createFetchHttpClient()
})

const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
const supabase = createClient(supabaseUrl, supabaseServiceKey)

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

serve(async (req) => {
  // ── CORS preflight ──
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  const url = new URL(req.url)
  const token = url.searchParams.get('token')

  // ================================================================
  // GET: Verificar token_aceptacion y devolver datos del presupuesto
  // ================================================================
  if (req.method === 'GET') {
    try {
      if (!token) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Token de aceptación requerido'
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // Buscar presupuesto por token_aceptacion
      const { data: presupuesto, error: presupuestoError } = await supabase
        .from('presupuestos')
        .select(`
          id,
          lead_id,
          tecnico_id,
          precio_total,
          descripcion,
          plazo_estimado,
          notas,
          estado,
          token_aceptacion,
          created_at,
          updated_at
        `)
        .eq('token_aceptacion', token)
        .maybeSingle()

      if (presupuestoError) {
        console.error('Error buscando presupuesto:', presupuestoError)
        return new Response(JSON.stringify({
          success: false,
          error: 'Error al verificar el presupuesto'
        }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      if (!presupuesto) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Enlace no válido o presupuesto no encontrado'
        }), {
          status: 404,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      if (presupuesto.estado !== 'enviado') {
        const mensaje = presupuesto.estado === 'pagado'
          ? 'Este presupuesto ya ha sido pagado'
          : presupuesto.estado === 'pendiente_pago'
          ? 'Este presupuesto está pendiente de pago'
          : 'Este presupuesto ya no está disponible'
        return new Response(JSON.stringify({
          success: false,
          error: mensaje,
          estado: presupuesto.estado
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // Obtener datos del lead asociado
      const { data: lead, error: leadError } = await supabase
        .from('leads')
        .select('id, nombre_cliente, zona, m2, tipo_inmueble, codigo_postal')
        .eq('id', presupuesto.lead_id)
        .maybeSingle()

      if (leadError || !lead) {
        console.error('Error obteniendo lead:', leadError)
        return new Response(JSON.stringify({
          success: false,
          error: 'Error al obtener datos del cliente'
        }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      return new Response(JSON.stringify({
        success: true,
        presupuesto: {
          id: presupuesto.id,
          precio_total: presupuesto.precio_total,
          descripcion: presupuesto.descripcion,
          plazo_estimado: presupuesto.plazo_estimado,
          notas: presupuesto.notas
        },
        lead: {
          nombre_cliente: lead.nombre_cliente,
          zona: lead.zona,
          m2: lead.m2,
          tipo_inmueble: lead.tipo_inmueble
        }
      }), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error desconocido'
      console.error('Error en GET aceptar-presupuesto:', message)
      return new Response(JSON.stringify({
        success: false,
        error: message
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
  }

  // ================================================================
  // POST: Cliente acepta y paga el presupuesto
  // ================================================================
  if (req.method === 'POST') {
    try {
      const body = await req.json()
      const { action, token: bodyToken, leadId, presupuesto_id } = body

      if (!action || action !== 'pagar') {
        return new Response(JSON.stringify({
          success: false,
          error: 'Acción no válida. Use action="pagar"'
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      if (!bodyToken || !presupuesto_id) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Faltan campos requeridos: token, presupuesto_id'
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // Verificar que el presupuesto existe y está en estado 'enviado'
      const { data: presupuesto, error: presupuestoError } = await supabase
        .from('presupuestos')
        .select('id, lead_id, tecnico_id, precio_total, descripcion, estado, token_aceptacion')
        .eq('id', presupuesto_id)
        .eq('token_aceptacion', bodyToken)
        .maybeSingle()

      if (presupuestoError) {
        console.error('Error verificando presupuesto:', presupuestoError)
        return new Response(JSON.stringify({
          success: false,
          error: 'Error al verificar el presupuesto'
        }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      if (!presupuesto) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Presupuesto no encontrado o token no válido'
        }), {
          status: 404,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      if (presupuesto.estado !== 'enviado') {
        return new Response(JSON.stringify({
          success: false,
          error: `El presupuesto ya no está disponible (estado: ${presupuesto.estado})`
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // Obtener datos del lead para el nombre del producto
      const { data: lead, error: leadError } = await supabase
        .from('leads')
        .select('nombre_cliente')
        .eq('id', presupuesto.lead_id)
        .maybeSingle()

      if (leadError || !lead) {
        console.error('Error obteniendo lead:', leadError)
        return new Response(JSON.stringify({
          success: false,
          error: 'Error al obtener datos del cliente'
        }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // Crear Stripe Checkout Session
      const priceInCents = Math.round(Number(presupuesto.precio_total) * 100)

      if (priceInCents <= 0) {
        return new Response(JSON.stringify({
          success: false,
          error: 'El importe del presupuesto no es válido'
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const session = await stripe.checkout.sessions.create({
        mode: 'payment',
        line_items: [{
          price_data: {
            currency: 'eur',
            product_data: {
              name: `Certificado energético - ${lead.nombre_cliente}`,
              description: presupuesto.descripcion || 'Certificado de Eficiencia Energética'
            },
            unit_amount: priceInCents
          },
          quantity: 1
        }],
        metadata: {
          tipo: 'pago_presupuesto',
          presupuesto_id: String(presupuesto.id),
          lead_id: String(presupuesto.lead_id),
          tecnico_id: String(presupuesto.tecnico_id)
        },
        success_url: `https://certificadoya.es/pago-exitoso.html?presupuesto_id=${presupuesto.id}`,
        cancel_url: 'https://certificadoya.es/'
      })

      // Actualizar presupuesto a 'pendiente_pago' y guardar stripe_session_id
      const { error: updateError } = await supabase
        .from('presupuestos')
        .update({
          estado: 'pendiente_pago',
          stripe_session_id: session.id,
          updated_at: new Date().toISOString()
        })
        .eq('id', presupuesto.id)

      if (updateError) {
        console.error('Error actualizando presupuesto:', updateError)
        // No retornamos error al cliente, la sesión ya se creó
      }

      return new Response(JSON.stringify({
        success: true,
        url: session.url,
        sessionId: session.id
      }), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error desconocido'
      console.error('Error en POST aceptar-presupuesto:', message)
      return new Response(JSON.stringify({
        success: false,
        error: message
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
  }

  // ── Method not allowed ──
  return new Response(JSON.stringify({
    success: false,
    error: 'Method not allowed. Use GET or POST.'
  }), {
    status: 405,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  })
})
