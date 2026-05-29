import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

const PROJECT = 'wypgqpgjlookbhuaiyxa'

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

    const token = Deno.env.get('SB_MGMT_TOKEN')
    if (!token) {
      return new Response(JSON.stringify({ error: 'Error de configuración' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Build the INSERT SQL directly - no function, just raw insert
    const esc = (s: string) => `'${s.replace(/'/g, "''")}'`
    const num = (v: number | undefined | null) => v != null ? Math.round(Number(v)).toString() : 'null'

    const sql = `INSERT INTO leads (nombre_cliente, telefono_cliente, email_cliente, codigo_postal, provincia, m2, tipo_inmueble, presupuesto_min, presupuesto_max, fuente)
VALUES (${esc(nombre)}, ${esc(telefono)}, ${(email || '').trim() ? esc((email || '').trim()) : 'null'}, ${esc(cpVal)}, ${(zona || '').trim() ? esc((zona || '').trim()) : 'null'}, ${num(m2)}, ${esc(tipo || 'piso')}, ${num(precioMin)}, ${num(precioMax)}, 'web')
RETURNING id;`

    const res = await fetch(
      `https://api.supabase.com/v1/projects/${PROJECT}/database/query`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query: sql })
      }
    )

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
      leadId: data?.[0]?.id,
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
