import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co'

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const body = await req.json()
    const { name, email, phone, cp, m2, tipo, zona, precioMin, precioMax } = body

    const nombre = (name || '').trim()
    const telefono = (phone || '').trim()
    const cpVal = (cp || '').trim()
    if (!nombre || !telefono || !cpVal) {
      return new Response(JSON.stringify({
        error: 'Faltan campos requeridos: nombre, teléfono y CP son obligatorios'
      }), {
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

    const emailVal = (email || '').trim() || null
    const zonaVal = (zona || '').trim() || null
    const m2Val = m2 != null ? Math.round(Number(m2)) : null
    const precioMinVal = precioMin != null ? Math.round(Number(precioMin)) : null
    const precioMaxVal = precioMax != null ? Math.round(Number(precioMax)) : null

    // INSERT directo en la tabla leads (evita RPC que no existe)
    const res = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': token,
        'Authorization': `Bearer ${token}`,
        'Prefer': 'return=representation'
      },
      body: JSON.stringify({
        nombre_cliente: nombre,
        telefono_cliente: telefono,
        email_cliente: emailVal,
        codigo_postal: cpVal,
        provincia: zonaVal,
        m2: m2Val,
        tipo_inmueble: tipo || 'piso',
        presupuesto_min: precioMinVal,
        presupuesto_max: precioMaxVal,
        fuente: 'web',
        estado: 'nuevo'
      })
    })

    const data = await res.json()

    if (!res.ok) {
      return new Response(JSON.stringify({
        error: data.message || JSON.stringify(data)
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    return new Response(JSON.stringify({
      success: true,
      leadId: data.id || data[0]?.id,
      mensaje: 'Solicitud recibida. Te contactaremos pronto.'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})