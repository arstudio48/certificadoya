import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

serve(async (req: Request) => {
  // Manejar CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { action, nombre_cliente, email_cliente, telefono_cliente, zona, m2, tipo_inmueble, presupuesto_min, presupuesto_max, fuente, estado, notas } = await req.json()

    // Solo aceptamos action='solicitar'
    if (action !== 'solicitar') {
      return new Response(JSON.stringify({ error: 'action no válida' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Validación mínima
    if (!nombre_cliente || !telefono_cliente || !zona) {
      return new Response(JSON.stringify({ error: 'Faltan campos requeridos: nombre, teléfono, zona' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co'
    const SUPABASE_KEY = Deno.env.get('SUPABASE_SERVICE_KEY')
    
    if (!SUPABASE_KEY) {
      return new Response(JSON.stringify({ error: 'Error de configuración del servidor' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Crear payload del lead
    const leadData = {
      nombre_cliente: nombre_cliente.trim(),
      email_cliente: email_cliente ? email_cliente.trim() : null,
      telefono_cliente: telefono_cliente.trim(),
      provincia: zona.trim(),
      m2: parseInt(m2) || null,
      tipo_inmueble: tipo_inmueble || 'piso',
      presupuesto_min: parseInt(presupuesto_min) || null,
      presupuesto_max: parseInt(presupuesto_max) || null,
      fuente: fuente || 'web-sin-pago',
      estado: estado || 'nuevo',
      notas: notas || null,
      created_at: new Date().toISOString()
    }

    // Insertar en Supabase
    const res = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Prefer': 'return=representation'
      },
      body: JSON.stringify(leadData)
    })

    // Si falla, devolver error
    if (!res.ok) {
      const errorData = await res.json()
      console.error('Error Supabase:', errorData)
      return new Response(JSON.stringify({ 
        error: 'Error al guardar la solicitud',
        details: errorData.message || errorData
      }), {
        status: res.status,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Éxito
    const createdLead = await res.json()
    
    // Enviar email de confirmación (simple)
    const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')
    if (email_cliente && RESEND_API_KEY) {
      try {
        await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${RESEND_API_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            from: 'CertificadoYa <info@certificadoya.es>',
            to: email_cliente,
            subject: '✅ Tu solicitud ha sido recibida - CertificadoYa',
            html: `
              <div style="font-family:Arial,sans-serif;background:#f5f7f2;padding:20px">
                <div style="background:#fff;border-radius:12px;padding:30px;max-width:500px;margin:0 auto">
                  <h1 style="color:#16a34a;font-size:24px;margin:0 0 10px">✅ Solicitud recibida</h1>
                  <p style="color:#666;line-height:1.6">Hola ${nombre_cliente},</p>
                  <p style="color:#666;line-height:1.6">Hemos recibido tu solicitud sin pago. En las próximas 24 horas, un técnico certificador de tu zona te contactará para aceptar el encargo.</p>
                  <div style="background:#f0faf2;border:1px solid #dce8d0;border-radius:8px;padding:15px;margin:20px 0">
                    <p style="color:#1a2e1e;font-weight:bold;margin:0 0 10px">Resumen:</p>
                    <p style="color:#6b7b5e;margin:5px 0"><strong>Provincia:</strong> ${zona}</p>
                    <p style="color:#6b7b5e;margin:5px 0"><strong>Superficie:</strong> ${m2} m²</p>
                    <p style="color:#6b7b5e;margin:5px 0"><strong>Tipo:</strong> ${tipo_inmueble}</p>
                    <p style="color:#6b7b5e;margin:5px 0"><strong>Presupuesto:</strong> ${presupuesto_min}€</p>
                  </div>
                  <p style="color:#666;line-height:1.6">Pagas solo cuando recibas tu CEE. Sin compromiso previo.</p>
                  <p style="color:#999;font-size:12px;margin-top:20px">📞 Si tienes preguntas, llama al 641 45 00 68</p>
                </div>
              </div>
            `
          })
        })
      } catch (emailError) {
        console.error('Error enviando email:', emailError)
        // No fallar si el email no se envía
      }
    }

    return new Response(JSON.stringify({
      success: true,
      message: 'Solicitud recibida correctamente',
      lead_id: createdLead[0]?.id || 'sin-id'
    }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('Error:', error)
    return new Response(JSON.stringify({ 
      error: 'Error interno del servidor',
      message: error.message
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
