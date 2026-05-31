import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co'

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Método no permitido' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }

  try {
    const body = await req.json()
    const { email, userType, timestamp, source } = body

    // Validar email
    const emailClean = (email || '').trim().toLowerCase()
    if (!emailClean || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailClean)) {
      return new Response(JSON.stringify({ error: 'Email inválido' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Validar userType
    if (!userType || !['technician', 'owner'].includes(userType)) {
      return new Response(JSON.stringify({ error: 'Tipo de usuario inválido' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const token = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    if (!token) {
      return new Response(JSON.stringify({ error: 'Error de configuración del servidor' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Verificar si ya existe
    const checkRes = await fetch(
      `${SUPABASE_URL}/rest/v1/newsletter_subscribers?email=eq.${encodeURIComponent(emailClean)}&select=id,active`,
      {
        headers: {
          'apikey': token,
          'Authorization': `Bearer ${token}`
        }
      }
    )
    const existing = await checkRes.json()

    if (existing && existing.length > 0) {
      const sub = existing[0]
      if (sub.active) {
        return new Response(JSON.stringify({
          success: true,
          message: 'Ya estás suscrito',
          alreadySubscribed: true
        }), {
          status: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }
      // Reactivar si estaba inactivo
      await fetch(`${SUPABASE_URL}/rest/v1/newsletter_subscribers?id=eq.${sub.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'apikey': token,
          'Authorization': `Bearer ${token}`,
          'Prefer': 'return=representation'
        },
        body: JSON.stringify({
          active: true,
          user_type: userType,
          source: source || 'website'
        })
      })
      return new Response(JSON.stringify({ success: true, message: 'Suscripción reactivada' }), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Insertar nuevo suscriptor
    const insertRes = await fetch(`${SUPABASE_URL}/rest/v1/newsletter_subscribers`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': token,
        'Authorization': `Bearer ${token}`,
        'Prefer': 'return=representation'
      },
      body: JSON.stringify({
        email: emailClean,
        user_type: userType,
        source: source || 'website',
        confirmed: true
      })
    })

    if (!insertRes.ok) {
      const errText = await insertRes.text()
      console.error('Error insertando suscriptor:', errText)
      return new Response(JSON.stringify({ error: 'Error al guardar la suscripción' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    return new Response(JSON.stringify({ success: true, message: 'Suscripción creada' }), {
      status: 201,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (err) {
    console.error('Error en newsletter-subscribe:', err)
    return new Response(JSON.stringify({ error: 'Error interno del servidor' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
