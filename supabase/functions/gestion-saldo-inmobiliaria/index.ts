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

// Precios: 5 créditos x 45€ = 225€, 10 créditos x 39€ = 390€, 20 créditos x 35€ = 700€
const PRECIOS: Record<number, { precio_unitario: number }> = {
  5:  { precio_unitario: 45 },
  10: { precio_unitario: 39 },
  20: { precio_unitario: 35 },
}

const CANTIDADES_VALIDAS = new Set([5, 10, 20])

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

    // Look up inmobiliaria by token
    const { data: inmo, error: inmoError } = await supabase
      .from('inmobiliarias')
      .select('id, email, nombre, token, saldo_creditos')
      .eq('token', token)
      .maybeSingle()

    if (inmoError || !inmo) {
      return new Response(JSON.stringify({ error: 'Inmobiliaria no encontrada' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const body = await req.json()
    const { action } = body

    // ============================================================
    // ACTION: comprar — Comprar créditos
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

      const precioUnitario = PRECIOS[cantidad].precio_unitario
      const importeTotal = cantidad * precioUnitario

      const session = await stripe.checkout.sessions.create({
        payment_method_types: ['card'],
        mode: 'payment',
        line_items: [{
          price_data: {
            currency: 'eur',
            product_data: {
              name: `${cantidad} créditos para propiedades`,
              description: `${cantidad} créditos × ${precioUnitario}€/crédito = ${importeTotal}€`,
            },
            unit_amount: importeTotal * 100,
          },
          quantity: 1,
        }],
        metadata: {
          tipo: 'compra_creditos_inmobiliaria',
          inmobiliaria_id: String(inmo.id),
          cantidad_creditos: String(cantidad),
          importe_total: String(importeTotal),
        },
        success_url: 'https://certificadoya.es/inmobiliarias/panel.html?creditos_ok=1',
        cancel_url: 'https://certificadoya.es/inmobiliarias/panel.html',
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
    // ACTION: saldo — Consultar créditos restantes
    // ============================================================
    if (action === 'saldo') {
      return new Response(JSON.stringify({
        success: true,
        saldo_creditos: inmo.saldo_creditos,
        nombre: inmo.nombre,
        email: inmo.email,
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ============================================================
    // ACTION: usar — Restar 1 crédito (al añadir propiedad)
    // ============================================================
    if (action === 'usar') {
      if (!inmo.saldo_creditos || inmo.saldo_creditos < 1) {
        return new Response(JSON.stringify({
          error: 'Sin créditos suficientes. Compra más créditos para añadir propiedades.',
          success: false,
          saldo_creditos: inmo.saldo_creditos || 0,
        }), {
          status: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const nuevoSaldo = inmo.saldo_creditos - 1
      const { error: updateError } = await supabase
        .from('inmobiliarias')
        .update({ saldo_creditos: nuevoSaldo })
        .eq('id', inmo.id)

      if (updateError) {
        console.error('Error updating saldo:', updateError)
        return new Response(JSON.stringify({ error: 'Error al actualizar saldo' }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // Registrar transacción
      await supabase
        .from('transacciones_inmobiliarias')
        .insert({
          inmobiliaria_id: inmo.id,
          tipo: 'gasto',
          cantidad: 1,
          concepto: 'Propiedad añadida',
          saldo_resultante: nuevoSaldo,
        })
        .maybeSingle()

      return new Response(JSON.stringify({
        success: true,
        saldo_creditos: nuevoSaldo,
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ============================================================
    // ACTION: historial — Transacciones de la inmobiliaria
    // ============================================================
    if (action === 'historial') {
      const limite = Math.min(Math.max(body.limite || 20, 1), 100)

      const { data: transacciones, error: transError } = await supabase
        .from('transacciones_inmobiliarias')
        .select('*')
        .eq('inmobiliaria_id', inmo.id)
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
      error: `Acción desconocida: "${action}". Acciones válidas: comprar, saldo, usar, historial`
    }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('Error en gestion-saldo-inmobiliaria:', error)
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
