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

const COSTO_POR_CREDITO = 4
const PRECIO_PREMIUM_MENSUAL = parseFloat(Deno.env.get('PRECIO_PREMIUM_MENSUAL') || '49.99')

const CANTIDADES_VALIDAS = new Set([5, 10, 15, 20, 25, 30])

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }

  try {
    // ── Auth: get token from Authorization header ──
    const authHeader = req.headers.get('authorization') || ''
    if (!authHeader.startsWith('Bearer ')) {
      return new Response(JSON.stringify({ error: 'Token requerido' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const token = authHeader.slice(7).trim()
    if (!token) {
      return new Response(JSON.stringify({ error: 'Token inválido' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Look up técnico by token
    const { data: tecnico, error: tecError } = await supabase
      .from('tecnicos')
      .select('id, email, nombre, token, modelo_pago, saldo_creditos, comision_por_lead, stripe_customer_id, stripe_subscription_id, premium_hasta')
      .eq('token', token)
      .maybeSingle()

    if (tecError || !tecnico) {
      return new Response(JSON.stringify({ error: 'Técnico no encontrado' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const body = await req.json()
    const { action } = body

    // ============================================================
    // ACTION: comprar — Comprar créditos/leads
    // ============================================================
    if (action === 'comprar') {
      const cantidad = body.cantidad

      if (typeof cantidad !== 'number' || !CANTIDADES_VALIDAS.has(cantidad)) {
        return new Response(JSON.stringify({
          error: `Cantidad inválida. Valores permitidos: ${[...CANTIDADES_VALIDAS].join(', ')}`
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const importeTotal = cantidad * COSTO_POR_CREDITO

      const session = await stripe.checkout.sessions.create({
        payment_method_types: ['card'],
        mode: 'payment',
        line_items: [{
          price_data: {
            currency: 'eur',
            product_data: {
              name: `${cantidad} créditos para leads`,
            },
            unit_amount: importeTotal * 100,
          },
          quantity: 1,
        }],
        metadata: {
          tipo: 'compra_creditos',
          tecnico_id: String(tecnico.id),
          cantidad_creditos: String(cantidad),
          importe_total: String(importeTotal),
        },
        success_url: 'https://certificadoya.es/pool-encargos.html?creditos_ok=1',
        cancel_url: 'https://certificadoya.es/pool-encargos.html',
      })

      return new Response(JSON.stringify({
        success: true,
        url: session.url,
        sessionId: session.id,
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ============================================================
    // ACTION: suscribir — Suscripción premium mensual
    // ============================================================
    if (action === 'suscribir') {
      const session = await stripe.checkout.sessions.create({
        payment_method_types: ['card'],
        mode: 'subscription',
        line_items: [{
          price_data: {
            currency: 'eur',
            product_data: {
              name: 'Suscripción Premium Mensual',
            },
            unit_amount: Math.round(PRECIO_PREMIUM_MENSUAL * 100),
            recurring: {
              interval: 'month',
            },
          },
          quantity: 1,
        }],
        metadata: {
          tipo: 'suscripcion_premium',
          tecnico_id: String(tecnico.id),
        },
        success_url: 'https://certificadoya.es/pool-encargos.html?premium_ok=1',
        cancel_url: 'https://certificadoya.es/pool-encargos.html',
      })

      return new Response(JSON.stringify({
        success: true,
        url: session.url,
        sessionId: session.id,
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ============================================================
    // ACTION: saldo — Consultar saldo y estado
    // ============================================================
    if (action === 'saldo') {
      return new Response(JSON.stringify({
        success: true,
        modelo_pago: tecnico.modelo_pago,
        saldo_creditos: tecnico.saldo_creditos,
        premium_hasta: tecnico.premium_hasta,
        comision_por_lead: tecnico.comision_por_lead,
        nombre: tecnico.nombre,
        email: tecnico.email,
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ============================================================
    // ACTION: historial — Transacciones del técnico
    // ============================================================
    if (action === 'historial') {
      const limite = Math.min(Math.max(body.limite || 20, 1), 100)

      const { data: transacciones, error: transError } = await supabase
        .from('transacciones_tecnicos')
        .select('*')
        .eq('tecnico_id', tecnico.id)
        .order('created_at', { ascending: false })
        .limit(limite)

      if (transError) {
        console.error('Error fetching transactions:', transError)
        return new Response(JSON.stringify({ error: 'Error al obtener historial' }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      return new Response(JSON.stringify({
        success: true,
        transacciones: transacciones || [],
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ============================================================
    // Unknown action
    // ============================================================
    return new Response(JSON.stringify({
      error: `Acción desconocida: "${action}". Acciones válidas: comprar, suscribir, saldo, historial`
    }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('Error en gestion-saldo:', error)
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
