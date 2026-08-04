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
    const body = await req.json()
    const { action, nombre_cliente, email_cliente, telefono_cliente, zona, m2, tipo_inmueble, presupuesto_min, presupuesto_max, fuente, estado, notas, stripe_payment_id } = body

    console.log('[solicitar-servicio] Recibido:', { action, nombre_cliente, zona, email_cliente })

    // Solo aceptamos action='solicitar'
    if (action !== 'solicitar') {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'action no válida. Use action=solicitar' 
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Validación mínima
    if (!nombre_cliente || !telefono_cliente || !zona) {
      return new Response(JSON.stringify({ 
        success: false,
        error: 'Faltan campos requeridos: nombre_cliente, telefono_cliente, zona' 
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Obtener SERVICE KEY (disponible en Edge Functions)
    const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    if (!serviceKey) {
      console.error('[solicitar-servicio] ERROR: SUPABASE_SERVICE_ROLE_KEY no está configurado')
      return new Response(JSON.stringify({ 
        success: false,
        error: 'Error de configuración del servidor (SERVICE_KEY)'
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const SUPABASE_URL = Deno.env.get('SUPABASE_URL') || 'https://wypgqpgjlookbhuaiyxa.supabase.co'

    console.log('[solicitar-servicio] serviceKey length:', serviceKey ? serviceKey.length : 0)

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
      // ⚠️ ANTI-ELUSIÓN: sin pago confirmado (stripe_payment_id) el lead NO se auto-asigna.
      // Queda en 'pendiente_pago' (el cron solo asigna 'nuevo'), obligando al cliente a pagar
      // antes de que un técnico pueda contactarle y saltarse la comisión del 18%.
      estado: (stripe_payment_id || (body as any).payment_intent || (body as any).charge_id)
        ? (estado || 'nuevo')
        : 'pendiente_pago',
      stripe_payment_id: stripe_payment_id || (body as any).payment_intent || (body as any).charge_id || null,
      notas: notas || null,
      created_at: new Date().toISOString()
    }

    console.log('[solicitar-servicio] Enviando a Supabase:', leadData)

    // PASO 1: Insertar en Supabase usando SERVICE_KEY
    const insertRes = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': serviceKey,
        'Authorization': `Bearer ${serviceKey}`,
        'Prefer': 'return=representation'
      },
      body: JSON.stringify(leadData)
    })

    const insertResponseText = await insertRes.text()
    console.log('[solicitar-servicio] Response status:', insertRes.status)
    console.log('[solicitar-servicio] Response body:', insertResponseText)

    // Si falla, devolver error REAL
    if (!insertRes.ok) {
      try {
        const errorData = JSON.parse(insertResponseText)
        console.error('[solicitar-servicio] Error Supabase:', errorData)
        return new Response(JSON.stringify({ 
          success: false,
          error: 'Error al guardar el lead en base de datos',
          details: errorData.message || errorData
        }), {
          status: insertRes.status,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      } catch (_) {
        return new Response(JSON.stringify({ 
          success: false,
          error: 'Error al procesar respuesta de servidor',
          details: insertResponseText
        }), {
          status: insertRes.status,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }
    }

    // PASO 2: Parsear la respuesta (debe ser array con el lead creado)
    let createdLead
    try {
      const jsonResponse = JSON.parse(insertResponseText)
      createdLead = Array.isArray(jsonResponse) ? jsonResponse[0] : jsonResponse
    } catch (_) {
      console.error('[solicitar-servicio] No se pudo parsear respuesta JSON')
      createdLead = null
    }

    console.log('[solicitar-servicio] Lead creado:', createdLead)

    // PASO 3: Enviar email de confirmación (opcional, no bloquea el flujo)
    const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')
    if (email_cliente && RESEND_API_KEY) {
      try {
        console.log('[solicitar-servicio] Enviando email a:', email_cliente)
        const emailRes = await fetch('https://api.resend.com/emails', {
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
                  <p style="color:#666;line-height:1.6">Hemos recibido tu solicitud. En las próximas 24 horas, un técnico certificador de tu zona te contactará.</p>
                  <div style="background:#f0faf2;border:1px solid #dce8d0;border-radius:8px;padding:15px;margin:20px 0">
                    <p style="color:#1a2e1e;font-weight:bold;margin:0 0 10px">Resumen:</p>
                    <p style="color:#6b7b5e;margin:5px 0"><strong>Provincia:</strong> ${zona}</p>
                    <p style="color:#6b7b5e;margin:5px 0"><strong>Superficie:</strong> ${m2} m²</p>
                    <p style="color:#6b7b5e;margin:5px 0"><strong>Tipo:</strong> ${tipo_inmueble}</p>
                    <p style="color:#6b7b5e;margin:5px 0"><strong>Presupuesto:</strong> ${presupuesto_min}€</p>
                  </div>
                  <p style="color:#666;line-height:1.6">Pagas solo cuando recibas tu CEE.</p>
                  <p style="color:#999;font-size:12px;margin-top:20px">📞 Si tienes preguntas, llama al 641 45 00 68</p>
                </div>
              </div>
            `
          })
        })
        console.log('[solicitar-servicio] Email enviado, status:', emailRes.status)
      } catch (emailError) {
        console.error('[solicitar-servicio] Error enviando email:', emailError)
        // No bloquear si falla el email
      }
    }

    // PASO 4: Retornar ÉXITO
    return new Response(JSON.stringify({
      success: true,
      message: 'Solicitud recibida correctamente',
      lead_id: createdLead?.id || 'sin-id'
    }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('[solicitar-servicio] Error no capturado:', error)
    return new Response(JSON.stringify({ 
      success: false,
      error: 'Error interno del servidor',
      message: error instanceof Error ? error.message : String(error)
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
