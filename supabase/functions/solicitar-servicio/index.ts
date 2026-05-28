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

const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') || ''

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  const url = new URL(req.url)
  const action = url.searchParams.get('action')

  // ============================================================
  // ACTION: solicitar — Guardar lead SIN cobro, notificar técnicos
  // ============================================================
  if (action === 'solicitar' || !action) {
    try {
      const { name, email, phone, cp, m2, tipo, zona, precioMin, precioMax, descripcion } = await req.json()

      if (!name || !phone || !cp) {
        return new Response(JSON.stringify({ error: 'Nombre, teléfono y CP son obligatorios' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // 1. Guardar lead en Supabase con estado 'pendiente'
      const lead = {
        nombre_cliente: name,
        telefono_cliente: phone,
        email_cliente: email || '',
        codigo_postal: cp,
        zona: zona || '',
        m2: m2 ? parseInt(m2) : null,
        tipo_inmueble: tipo || '',
        presupuesto_min: precioMin ? parseInt(precioMin) : null,
        presupuesto_max: precioMax ? parseInt(precioMax) : null,
        estado: 'pendiente',
        fuente: 'web'
      }

      const { data: leadData, error: insertError } = await supabase
        .from('leads')
        .insert([lead])
        .select()
        .single()

      if (insertError) {
        console.error('Error saving lead:', insertError)
        return new Response(JSON.stringify({ error: 'Error al guardar la solicitud' }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // 2. Buscar técnicos en la misma provincia (por CP)
      const provinciaCP = cp.substring(0, 2)
      const { data: tecnicos } = await supabase
        .from('tecnicos')
        .select('email, nombre, telefono')
        .eq('activo', true)
        .or(`provincia.ilike.%${provinciaCP}%`)

      // 3. Notificar técnicos disponibles por email
      const tecnicosNotificados: string[] = []
      if (tecnicos && tecnicos.length > 0) {
        const leadId = leadData?.id
        const textoLead = `
          <div style="font-family: sans-serif; max-width: 560px; margin: 0 auto;">
            <h2 style="color: #547c24;">🆕 Nuevo cliente disponible</h2>
            <table style="width: 100%; border-collapse: collapse;">
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Cliente</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${name}</td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Teléfono</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${phone}</td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Email</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${email || '—'}</td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Zona</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${zona || '—'} (CP: ${cp})</td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Inmueble</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${m2 || '?'} m² - ${tipo || '—'}</td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Presupuesto</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${precioMin || '?'}€ — ${precioMax || '?'}€</td></tr>
            </table>
            <div style="margin: 20px 0; text-align: center;">
              <a href="https://certificadoya.es/aceptar-encargo.html?lead=${leadId}&tec=${encodeURIComponent('{{EMAIL}}')}"
                 style="display: inline-block; background: #547c24; color: white; padding: 12px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px;">
                ✅ Aceptar encargo
              </a>
            </div>
            <p style="color: #999; font-size: 12px;">El cliente aún no ha pagado. Solo se cobrará si aceptas el encargo.</p>
          </div>
        `

        for (const tecnico of tecnicos) {
          try {
            if (tecnico.email) {
              await fetch('https://api.resend.com/emails', {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${RESEND_API_KEY}`,
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  from: 'CertificadoYa <info@certificadoya.es>',
                  to: tecnico.email,
                  subject: `🆕 Nuevo cliente en ${zona || 'tu zona'} — CertificadoYa`,
                  html: textoLead.replace('{{EMAIL}}', encodeURIComponent(tecnico.email))
                })
              })
              tecnicosNotificados.push(tecnico.email)
            }
          } catch (_) { /* fallo email no crítico */ }
        }
      }

      // 4. Notificar al admin
      try {
        await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${RESEND_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            from: 'CertificadoYa <info@certificadoya.es>',
            to: 'artbriher@gmail.com',
            subject: `🆕 Nueva solicitud — ${name} — ${zona || cp}`,
            html: `
              <h2 style="color: #547c24;">🆕 Nueva solicitud de servicio</h2>
              <p><strong>Cliente:</strong> ${name}</p>
              <p><strong>Teléfono:</strong> ${phone}</p>
              <p><strong>Email:</strong> ${email || '—'}</p>
              <p><strong>Zona:</strong> ${zona || '—'} (CP: ${cp})</p>
              <p><strong>Inmueble:</strong> ${m2 || '?'} m² - ${tipo || '—'}</p>
              <p><strong>Presupuesto:</strong> ${precioMin || '?'}€ — ${precioMax || '?'}€</p>
              <p><strong>Técnicos notificados:</strong> ${tecnicosNotificados.length}</p>
              ${tecnicosNotificados.length === 0 ? '<p style="color: red;">⚠️ No hay técnicos disponibles en esta zona</p>' : ''}
            `
          })
        })
      } catch (_) { /* email no crítico */ }

      return new Response(JSON.stringify({
        success: true,
        leadId: leadData?.id,
        tecnicosNotificados: tecnicosNotificados.length,
        mensaje: tecnicosNotificados.length > 0
          ? 'Solicitud enviada. Un técnico te contactará pronto.'
          : 'Solicitud enviada. No tenemos técnicos en tu zona ahora, pero te avisaremos cuando haya.'
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    } catch (error) {
      console.error('Error:', error)
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
  }

  // ============================================================
  // ACTION: aceptar — Técnico acepta encargo → cobrar al cliente
  // ============================================================
  if (action === 'aceptar') {
    try {
      const { leadId, tecnicoEmail } = await req.json()

      if (!leadId || !tecnicoEmail) {
        return new Response(JSON.stringify({ error: 'Faltan datos' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // Obtener lead de Supabase
      const { data: lead, error: leadError } = await supabase
        .from('leads')
        .select('*')
        .eq('id', leadId)
        .single()

      if (leadError || !lead) {
        return new Response(JSON.stringify({ error: 'Lead no encontrado' }), {
          status: 404,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      if (lead.estado !== 'pendiente') {
        return new Response(JSON.stringify({ error: 'Este encargo ya fue asignado a otro técnico' }), {
          status: 409,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // Cobrar al cliente con Stripe
      const precioCobro = lead.presupuesto_min || 45
      const session = await stripe.checkout.sessions.create({
        payment_method_types: ['card'],
        line_items: [{
          price_data: {
            currency: 'eur',
            product_data: {
              name: `Certificado energético - ${lead.zona || lead.codigo_postal || ''}`,
              description: `${lead.tipo_inmueble || 'Inmueble'} de ${lead.m2 || '?'} m²`
            },
            unit_amount: Math.round(precioCobro * 100)
          },
          quantity: 1
        }],
        mode: 'payment',
        success_url: `https://certificadoya.es/gracias.html?lead=${leadId}&tecnico=${encodeURIComponent(tecnicoEmail)}`,
        cancel_url: 'https://certificadoya.es/',
        metadata: {
          leadId: String(leadId),
          tecnicoEmail,
          clienteNombre: lead.nombre_cliente || '',
          clienteEmail: lead.email_cliente || '',
          clientePhone: lead.telefono_cliente || '',
          cp: lead.codigo_postal || '',
          m2: String(lead.m2 || ''),
          tipo: lead.tipo_inmueble || ''
        }
      })

      // Marcar lead como 'pendiente-pago'
      await supabase
        .from('leads')
        .update({ estado: 'pendiente-pago', tecnico_asignado: tecnicoEmail })
        .eq('id', leadId)

      return new Response(JSON.stringify({
        success: true,
        url: session.url,
        clienteNombre: lead.nombre_cliente,
        clienteTelefono: lead.telefono_cliente
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    } catch (error) {
      console.error('Error:', error)
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
  }

  // ============================================================
  // ACTION: confirmar-pago — Cliente pagó, notificar al técnico
  // ============================================================
  if (action === 'confirmar-pago') {
    try {
      const { session_id } = await req.json()
      if (!session_id) {
        return new Response(JSON.stringify({ error: 'Missing session_id' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const session = await stripe.checkout.sessions.retrieve(session_id)
      if (session.payment_status !== 'paid') {
        return new Response(JSON.stringify({ error: 'Payment not completed' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const meta = session.metadata || {}
      const leadId = meta.leadId
      const tecnicoEmail = meta.tecnicoEmail

      // Actualizar lead a 'pagado'
      if (leadId) {
        await supabase
          .from('leads')
          .update({ estado: 'pagado' })
          .eq('id', parseInt(leadId))
      }

      // Notificar al técnico
      if (tecnicoEmail) {
        try {
          await fetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${RESEND_API_KEY}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              from: 'CertificadoYa <info@certificadoya.es>',
              to: tecnicoEmail,
              subject: `💰 Cliente pagó — Datos de contacto`,
              html: `
                <h2 style="color: #547c24;">💰 Pago confirmado — Cliente tuyo</h2>
                <p>El cliente ya pagó. Aquí tienes sus datos:</p>
                <p><strong>Nombre:</strong> ${meta.clienteNombre || ''}</p>
                <p><strong>Teléfono:</strong> ${meta.clientePhone || ''}</p>
                <p><strong>Email:</strong> ${meta.clienteEmail || ''}</p>
                <p><strong>Dirección:</strong> CP ${meta.cp || ''}</p>
                <p><strong>Inmueble:</strong> ${meta.m2 || ''} m² (${meta.tipo || ''})</p>
                <p style="margin-top: 20px;">Contacta al cliente y realiza el certificado. ¡Gracias por trabajar con CertificadoYa!</p>
              `
            })
          })
        } catch (_) { /* email no crítico */ }
      }

      return new Response(JSON.stringify({ success: true }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    } catch (error) {
      console.error('Error:', error)
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
  }

  return new Response(JSON.stringify({ error: 'Unknown action' }), {
    status: 400,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  })
})
