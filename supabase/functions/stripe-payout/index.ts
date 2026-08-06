// Edge Function: stripe-payout
// Transfiere al técnico su parte (82%) tras completar el servicio
// Usa Stripe Connect si el técnico tiene cuenta vinculada
// Si no, registra como pago pendiente para gestión manual
// Deploy: supabase functions deploy stripe-payout --no-verify-jwt

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

const COMISION = 0.18 // 18% para CertificadoYa

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { lead_id, tecnico_id } = await req.json()
    if (!lead_id || !tecnico_id) {
      return new Response(JSON.stringify({ error: 'Faltan lead_id y tecnico_id' }), {
        status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Obtener datos del lead
    const { data: lead, error: leadErr } = await supabase
      .from('leads')
      .select('id, presupuesto_min, estado, tecnico_asignado, session_id')
      .eq('id', lead_id)
      .eq('tecnico_asignado', tecnico_id)
      .single()

    if (leadErr || !lead) {
      return new Response(JSON.stringify({ error: 'Lead no encontrado' }), {
        status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    if (lead.estado !== 'completado') {
      return new Response(JSON.stringify({ error: 'El lead debe estar en estado completado' }), {
        status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Obtener datos del técnico
    const { data: tecnico, error: tecErr } = await supabase
      .from('tecnicos')
      .select('id, nombre, email, stripe_account_id')
      .eq('id', tecnico_id)
      .single()

    if (tecErr || !tecnico) {
      return new Response(JSON.stringify({ error: 'Técnico no encontrado' }), {
        status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const total = lead.presupuesto_min || 0
    const comision = Math.round(total * COMISION * 100) / 100
    const tecnicoRecibe = total - comision

    // Guardar registro de pago
    const pago = {
      lead_id: lead_id,
      tecnico_id: tecnico_id,
      total: total,
      comision: comision,
      tecnico_recibe: tecnicoRecibe,
      estado: tecnico.stripe_account_id ? 'procesando' : 'pendiente',
      metodo: tecnico.stripe_account_id ? 'stripe_connect' : 'manual',
      created_at: new Date().toISOString()
    }

    const { error: insertErr } = await supabase.from('pagos_tecnicos').insert([pago])
    if (insertErr) console.error('Error guardando pago:', insertErr)

    // Stripe Connect: transferir al técnico
    if (tecnico.stripe_account_id) {
      try {
        await stripe.transfers.create({
          amount: Math.round(tecnicoRecibe * 100),
          currency: 'eur',
          destination: tecnico.stripe_account_id,
          transfer_group: `lead_${lead_id}`,
          metadata: {
            lead_id: String(lead_id),
            tecnico_id: String(tecnico_id),
            tipo: 'comision_servicio'
          }
        })

        await supabase.from('pagos_tecnicos')
          .update({ estado: 'completado', transferido_at: new Date().toISOString() })
          .eq('lead_id', lead_id)

        return new Response(JSON.stringify({
          success: true,
          metodo: 'stripe_connect',
          tecnico_recibe: tecnicoRecibe,
          comision: comision
        }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })

      } catch (stripeErr) {
        console.error('Error Stripe Connect:', stripeErr)
        await supabase.from('pagos_tecnicos')
          .update({ estado: 'error', error_msg: String(stripeErr) })
          .eq('lead_id', lead_id)
      }
    }

    // Fallback manual
    return new Response(JSON.stringify({
      success: true,
      metodo: 'manual',
      tecnico_recibe: tecnicoRecibe,
      comision: comision,
      mensaje: 'Pago registrado como pendiente. Revisa la tabla pagos_tecnicos para transferir manualmente.'
    }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
