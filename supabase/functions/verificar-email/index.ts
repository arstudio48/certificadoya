import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co'

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const body = await req.json()
    const { token, email } = body

    if (!token || !email) {
      return new Response(JSON.stringify({
        success: false,
        message: 'Faltan parámetros: token y email son obligatorios'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    if (!serviceKey) {
      return new Response(JSON.stringify({
        success: false,
        message: 'Error de configuración del servidor'
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Buscar lead con ese token y email
    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/leads?token_verificacion=eq.${encodeURIComponent(token)}&email_cliente=eq.${encodeURIComponent(email)}&select=id,estado,email_verificado`,
      {
        headers: {
          'apikey': serviceKey,
          'Authorization': `Bearer ${serviceKey}`
        }
      }
    )

    const leads = await res.json()

    if (!Array.isArray(leads) || leads.length === 0) {
      return new Response(JSON.stringify({
        success: false,
        message: 'Token inválido o expirado'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const lead = leads[0]

    if (lead.email_verificado) {
      return new Response(JSON.stringify({
        success: true,
        message: 'Email ya verificado anteriormente'
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    if (lead.estado !== 'pendiente_verificacion') {
      return new Response(JSON.stringify({
        success: false,
        message: 'El lead no está en estado pendiente de verificación'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Actualizar: marcar como verificado, cambiar estado a pendiente, limpiar token
    const now = new Date().toISOString()
    const updateRes = await fetch(
      `${SUPABASE_URL}/rest/v1/leads?id=eq.${encodeURIComponent(lead.id)}`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'apikey': serviceKey,
          'Authorization': `Bearer ${serviceKey}`,
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify({
          email_verificado: true,
          email_verificado_en: now,
          estado: 'pendiente',
          token_verificacion: null
        })
      }
    )

    if (!updateRes.ok) {
      const errText = await updateRes.text()
      console.error('Error al actualizar lead:', errText)
      return new Response(JSON.stringify({
        success: false,
        message: 'Error al verificar el email. Inténtalo de nuevo.'
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    return new Response(JSON.stringify({
      success: true,
      message: 'Email verificado correctamente. Tu solicitud está siendo procesada.'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error: any) {
    return new Response(JSON.stringify({
      success: false,
      message: error.message || 'Error interno del servidor'
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
