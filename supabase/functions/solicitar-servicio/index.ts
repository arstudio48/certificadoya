import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') ?? ''
const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co'

/** Calcula advertencias sobre datos faltantes en el lead */
function calcularAvisos(lead: Record<string, any>): string[] {
  const avisos: string[] = []
  if (!lead.telefono_cliente && !lead.phone) avisos.push('Falta teléfono del cliente — el técnico no podrá contactar por llamada')
  if (!lead.codigo_postal && !lead.cp) avisos.push('Falta código postal — la zona de cobertura es imprecisa')
  if (!lead.email_cliente && !lead.email) avisos.push('Falta email del cliente — no se puede enviar confirmación')
  if (!lead.nombre_cliente && !lead.name) avisos.push('Falta nombre del cliente — el técnico no sabe a quién contactar')
  return avisos
}

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const body = await req.json()

    // Aceptamos ambos naming conventions (inglés/español)
    const {
      action, name, email, phone, cp, m2, tipo, zona, precioMin, precioMax, leadId,
      nombre_cliente, email_cliente, telefono_cliente, codigo_postal,
      tipo_inmueble, provincia, presupuesto_min, presupuesto_max, fuente, estado
    } = body

    // Normalizar campos
    const nombre       = (name || nombre_cliente || '').trim()
    const emailVal     = (email || email_cliente || '').trim() || null
    const telefono     = (phone || telefono_cliente || '').trim()
    const cpVal        = (cp || codigo_postal || '').trim()
    const zonaVal      = (zona || provincia || '').trim()
    const tipoVal      = tipo || tipo_inmueble || 'piso'
    const precioMinVal = precioMin ?? presupuesto_min ?? null
    const precioMaxVal = precioMax ?? presupuesto_max ?? null
    const fuenteVal    = (fuente || 'web').trim()
    const estadoVal    = estado || 'pendiente'

    // Detectar si es lead desde calculadora (soft capture, puede no tener teléfono)
    const esCalculadora = fuenteVal.startsWith('web-f1') || fuenteVal.includes('calculadora')

    if (action === 'solicitar') {
      // Ruta llamada desde el frontend después de guardar lead — notificar a técnicos
      // (actualmente no implementada, solo respuesta de éxito)
      return new Response(JSON.stringify({ success: true }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    if (action === 'aceptar') {
      const token = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
      if (!token) {
        return new Response(JSON.stringify({ error: 'Error de configuración del servidor' }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const tecnicoEmail = body.tecnicoEmail
      const leadIdVal = body.leadId

      if (!tecnicoEmail || !leadIdVal) {
        return new Response(JSON.stringify({ error: 'Faltan campos requeridos: leadId y tecnicoEmail' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // a) Buscar técnico por email
      const tecRes = await fetch(`${SUPABASE_URL}/rest/v1/tecnicos?email=eq.${encodeURIComponent(tecnicoEmail)}&select=*`, {
        headers: {
          'apikey': token,
          'Authorization': `Bearer ${token}`
        }
      })
      const tecData = await tecRes.json()
      const tecnico = Array.isArray(tecData) ? tecData[0] : null

      if (!tecnico || !tecnico.activo) {
        return new Response(JSON.stringify({ error: 'Técnico no encontrado o no activo' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // c) Buscar lead
      const leadRes = await fetch(`${SUPABASE_URL}/rest/v1/leads?id=eq.${encodeURIComponent(leadIdVal)}&select=*`, {
        headers: {
          'apikey': token,
          'Authorization': `Bearer ${token}`
        }
      })
      const leadData = await leadRes.json()
      const lead = Array.isArray(leadData) ? leadData[0] : null

      if (!lead) {
        return new Response(JSON.stringify({ error: 'Lead no encontrado' }), {
          status: 404,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // d) Verificar estado válido
      if (lead.estado !== 'nuevo' && lead.estado !== 'pendiente') {
        return new Response(JSON.stringify({ error: `El lead ya está en estado "${lead.estado}" y no puede ser asignado` }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // d2) Calcular advertencias sobre datos faltantes
      const avisos = calcularAvisos(lead)

      // e) Modelo de pago 'lead': verificar saldo, descontar 1 crédito, registrar transacción
      if (tecnico.modelo_pago === 'lead') {
        if (!tecnico.saldo_creditos || tecnico.saldo_creditos <= 0) {
          return new Response(JSON.stringify({ error: 'Saldo de créditos insuficiente' }), {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          })
        }

        const nuevoSaldo = (tecnico.saldo_creditos || 0) - 1
        await fetch(`${SUPABASE_URL}/rest/v1/tecnicos?id=eq.${encodeURIComponent(tecnico.id)}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'apikey': token,
            'Authorization': `Bearer ${token}`,
            'Prefer': 'return=minimal'
          },
          body: JSON.stringify({ saldo_creditos: nuevoSaldo })
        })

        await fetch(`${SUPABASE_URL}/rest/v1/transacciones_tecnicos`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'apikey': token,
            'Authorization': `Bearer ${token}`,
            'Prefer': 'return=minimal'
          },
          body: JSON.stringify({
            tecnico_id: tecnico.id,
            tipo: 'gasto_lead',
            cantidad: -1,
            concepto: `Gasto por aceptar lead #${leadIdVal}`
          })
        })
      } else if (tecnico.modelo_pago === 'premium') {
        // f) Modelo premium: verificar vigencia
        const premiumHasta = new Date(tecnico.premium_hasta)
        if (premiumHasta <= new Date()) {
          return new Response(JSON.stringify({ error: 'Suscripción premium expirada' }), {
            status: 400,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          })
        }
        // Premium: asignar sin descontar créditos
      } else {
        return new Response(JSON.stringify({ error: 'Modelo de pago no válido' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // g) Actualizar lead: estado='asignado', tecnico_asignado_id, fecha_asignacion
      const now = new Date().toISOString()
      await fetch(`${SUPABASE_URL}/rest/v1/leads?id=eq.${encodeURIComponent(leadIdVal)}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'apikey': token,
          'Authorization': `Bearer ${token}`,
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify({
          estado: 'asignado',
          tecnico_asignado: tecnico.id,
          fecha_asignacion: now
        })
      })

      // Función para construir HTML de avisos
      const htmlAvisos = avisos.length > 0
        ? `<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:12px 16px;margin:0 40px 20px">
             <p style="font-size:13px;color:#856404;margin:0 0 6px;font-weight:600">⚠️ Datos incompletos del cliente</p>
             <ul style="margin:0;padding-left:18px;font-size:13px;color:#856404">
               ${avisos.map(a => `<li>${a}</li>`).join('')}
             </ul>
           </div>`
        : ''

      // h) NOTIFICAR al técnico por email
      if (RESEND_API_KEY) {
        await fetch("https://api.resend.com/emails", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${RESEND_API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            from: "CertificadoYa <info@certificadoya.es>",
            to: tecnico.email,
            subject: `🔔 Nuevo lead asignado #${leadIdVal}${avisos.length > 0 ? ' ⚠️' : ''}`,
            html: `
              <div style="font-family:Outfit,'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f7f2;padding:30px 15px">
                <div style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)">
                  <div style="background:linear-gradient(135deg,#547c24,#3d5e1a);padding:30px 40px;text-align:center">
                    <div style="font-size:28px;font-weight:700;color:#fff">CertificadoYa</div>
                    <div style="font-size:13px;color:#b8d4a0;margin-top:4px">Nuevo Lead Asignado</div>
                  </div>
                  <div style="padding:35px 40px 10px">
                    <div style="font-size:48px;text-align:center;margin-bottom:10px">🔔</div>
                    <h1 style="font-size:22px;font-weight:700;color:#1a1a1a;margin:0 0 6px;text-align:center">¡Tienes un nuevo lead!</h1>
                    <p style="font-size:15px;color:#6b7b5e;line-height:1.5;text-align:center">Se te ha asignado un nuevo cliente. <strong>Contacta con él lo antes posible.</strong></p>
                  </div>
                  ${htmlAvisos}
                  <div style="padding:10px 40px 20px">
                    <div style="background:#f3f9eb;border-radius:8px;padding:16px 20px">
                      <p style="font-size:13px;color:#5a7a3a;margin:0 0 10px;font-weight:600">📋 Datos del cliente</p>
                      <table style="width:100%;border-collapse:collapse;font-size:13px">
                        <tr><td style="padding:4px 0;color:#6b7b5e">Nombre</td><td style="padding:4px 0;color:#1a1a1a;font-weight:600">${lead.nombre_cliente || lead.name || '—'}</td></tr>
                        <tr><td style="padding:4px 0;color:#6b7b5e">Teléfono</td><td style="padding:4px 0;color:#1a1a1a">${lead.telefono_cliente || lead.phone || '⚠️ No disponible'}</td></tr>
                        <tr><td style="padding:4px 0;color:#6b7b5e">Email</td><td style="padding:4px 0;color:#1a1a1a">${lead.email_cliente || lead.email || '—'}</td></tr>
                        <tr><td style="padding:4px 0;color:#6b7b5e">Zona</td><td style="padding:4px 0;color:#1a1a1a">${lead.provincia || lead.zona || '—'} ${lead.codigo_postal ? '(CP: ' + lead.codigo_postal + ')' : '⚠️ Sin CP'}</td></tr>
                        <tr><td style="padding:4px 0;color:#6b7b5e">Inmueble</td><td style="padding:4px 0;color:#1a1a1a">${lead.m2 || '—'} m² · ${lead.tipo_inmueble || 'Piso'}</td></tr>
                        <tr><td style="padding:4px 0;color:#6b7b5e">Fuente</td><td style="padding:4px 0;color:#1a1a1a">${lead.fuente || 'web'}</td></tr>
                      </table>
                    </div>
                  </div>
                  ${avisos.length > 0
                    ? `<div style="padding:0 40px 10px">
                         <p style="font-size:13px;color:#856404;line-height:1.5;background:#fff8e6;padding:12px 16px;border-radius:8px;border-left:4px solid #ffc107">
                           ⚠️ Este lead tiene datos incompletos. Contacta con el cliente para obtener la información que falta antes de proceder.
                         </p>
                       </div>`
                    : ''}
                  <div style="padding:0 40px 25px;text-align:center">
                    <p style="font-size:14px;color:#6b7b5e;line-height:1.5">Accede a tu panel para gestionar este y otros leads:</p>
                    <a href="https://www.certificadoya.es/panel-tecnico/" style="display:inline-block;background:#547c24;color:#fff;text-decoration:none;padding:10px 24px;border-radius:8px;font-weight:600;font-size:14px">Ir al panel →</a>
                  </div>
                  <div style="padding:20px 40px;text-align:center;font-size:12px;color:#9aab8a;border-top:1px solid #eef4e8">
                    <p style="margin:0 0 4px">CertificadoYa.es — Certificación energética en toda España</p>
                    <p style="margin:0"><a href="https://www.certificadoya.es/" style="color:#547c24">certificadoya.es</a> · <a href="mailto:info@certificadoya.es" style="color:#547c24">info@certificadoya.es</a></p>
                  </div>
                </div>
              </div>
            `,
          }),
        }).catch(e => console.error("Error notificando al técnico:", e));
      }

      // i) NOTIFICAR al cliente por email (con avisos si faltan datos)
      if (lead.email_cliente && RESEND_API_KEY) {
        await fetch("https://api.resend.com/emails", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${RESEND_API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            from: "CertificadoYa <info@certificadoya.es>",
            to: lead.email_cliente,
            subject: `✅ Solicitud aceptada - CertificadoYa`,
            html: `
              <div style="font-family:Outfit,'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f7f2;padding:30px 15px">
                <div style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)">
                  <div style="background:linear-gradient(135deg,#547c24,#3d5e1a);padding:30px 40px;text-align:center">
                    <div style="font-size:28px;font-weight:700;color:#fff">CertificadoYa</div>
                    <div style="font-size:13px;color:#b8d4a0;margin-top:4px">Solicitud Aceptada</div>
                  </div>
                  <div style="padding:35px 40px 10px">
                    <div style="font-size:48px;text-align:center;margin-bottom:10px">✅</div>
                    <h1 style="font-size:22px;font-weight:700;color:#1a1a1a;margin:0 0 6px;text-align:center">¡Tu solicitud ha sido aceptada!</h1>
                    <p style="font-size:15px;color:#6b7b5e;line-height:1.5;text-align:center"><strong>${tecnico.nombre}</strong> se pondrá en contacto contigo pronto para realizar el certificado energético de tu vivienda.</p>
                  </div>
                  ${htmlAvisos}
                  <div style="padding:10px 40px 20px">
                    <div style="background:#f3f9eb;border-radius:8px;padding:16px 20px">
                      <p style="font-size:13px;color:#5a7a3a;margin:0 0 10px;font-weight:600">🔧 Técnico asignado</p>
                      <table style="width:100%;border-collapse:collapse;font-size:13px">
                        <tr><td style="padding:4px 0;color:#6b7b5e">Nombre</td><td style="padding:4px 0;color:#1a1a1a;font-weight:600">${tecnico.nombre}</td></tr>
                        <tr><td style="padding:4px 0;color:#6b7b5e">Teléfono</td><td style="padding:4px 0;color:#1a1a1a">${tecnico.telefono || '—'}</td></tr>
                        <tr><td style="padding:4px 0;color:#6b7b5e">Email</td><td style="padding:4px 0;color:#1a1a1a">${tecnico.email}</td></tr>
                      </table>
                    </div>
                  </div>
                  <div style="padding:0 40px 25px;text-align:center">
                    <p style="font-size:14px;color:#6b7b5e;line-height:1.5">Si no recibes noticias en las próximas 24 horas, puedes contactarnos en <a href="mailto:info@certificadoya.es" style="color:#547c24">info@certificadoya.es</a>.</p>
                  </div>
                  <div style="padding:20px 40px;text-align:center;font-size:12px;color:#9aab8a;border-top:1px solid #eef4e8">
                    <p style="margin:0 0 4px">CertificadoYa.es — Certificación energética en toda España</p>
                    <p style="margin:0"><a href="https://www.certificadoya.es/" style="color:#547c24">certificadoya.es</a> · <a href="mailto:info@certificadoya.es" style="color:#547c24">info@certificadoya.es</a></p>
                  </div>
                </div>
              </div>
            `,
          }),
        }).catch(e => console.error("Error notificando al cliente:", e));
      }

      // j) Devolver respuesta al frontend
      return new Response(JSON.stringify({
        success: true,
        leadId: leadIdVal,
        avisos: avisos.length > 0 ? avisos : undefined,
        incompleto: avisos.length > 0,
        tecnico: {
          nombre: tecnico.nombre,
          email: tecnico.email,
          telefono: tecnico.telefono || ''
        }
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ==== CREAR LEAD (action no especificada o desconocida) ====

    // Validación flexible: si es calculadora, solo requiere nombre/email
    // Si es lead completo, requiere nombre + teléfono + CP
    if (esCalculadora) {
      if (!nombre) {
        return new Response(JSON.stringify({
          error: 'Faltan campos requeridos: nombre del cliente (email) es obligatorio'
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }
    } else {
      if (!nombre || !telefono || !cpVal) {
        return new Response(JSON.stringify({
          error: 'Faltan campos requeridos: nombre, teléfono y CP son obligatorios'
        }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }
    }

    const token = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    if (!token) {
      return new Response(JSON.stringify({ error: 'Error de configuración del servidor' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const m2Val = m2 != null ? Math.round(Number(m2)) : null
    const pMinVal = precioMinVal != null ? Math.round(Number(precioMinVal)) : null
    const pMaxVal = precioMaxVal != null ? Math.round(Number(precioMaxVal)) : null

    // Generar token de verificación si tiene email
    const tokenVerificacion = emailVal ? crypto.randomUUID() : null
    const estadoLead = emailVal ? 'pendiente_verificacion' : estadoVal

    // Calcular advertencias pre-creación
    const avisosPre = calcularAvisos({ telefono_cliente: telefono, codigo_postal: cpVal, email_cliente: emailVal, nombre_cliente: nombre })
      .filter(a => !a.includes('nombre')) // nombre siempre está presente aunque sea el email

    // INSERT directo en la tabla leads
    const leadPayload: Record<string, any> = {
      nombre_cliente: nombre,
      telefono_cliente: telefono || null,
      email_cliente: emailVal,
      codigo_postal: cpVal || null,
      provincia: zonaVal || null,
      m2: m2Val,
      tipo_inmueble: tipoVal,
      presupuesto_min: pMinVal,
      presupuesto_max: pMaxVal,
      fuente: fuenteVal,
      estado: estadoLead,
      email_verificado: false,
      token_verificacion: tokenVerificacion
    }

    const res = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': token,
        'Authorization': `Bearer ${token}`,
        'Prefer': 'return=representation'
      },
      body: JSON.stringify(leadPayload)
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

    // --- Enviar email de verificación (si tiene email) ---
    if (emailVal && tokenVerificacion && RESEND_API_KEY) {
      const linkVerificacion = `https://www.certificadoya.es/verificar-email.html?token=${encodeURIComponent(tokenVerificacion)}&email=${encodeURIComponent(emailVal)}`

      // Añadir avisos al email de verificación si faltan datos
      const avisosEmail = avisosPre.length > 0
        ? `<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:12px 16px;margin:20px 40px">
             <p style="font-size:13px;color:#856404;margin:0 0 6px;font-weight:600">📝 Completa tus datos</p>
             <p style="font-size:13px;color:#856404;margin:0;line-height:1.5">Para que un técnico pueda contactarte sin problemas, te recomendamos que nos proporciones también:</p>
             <ul style="margin:6px 0 0;padding-left:18px;font-size:13px;color:#856404">
               ${avisosPre.map(a => `<li style="margin-bottom:2px">${a.replace('Falta ', '')}</li>`).join('')}
             </ul>
             <p style="font-size:13px;color:#856404;margin:8px 0 0">Puedes responder a este email con tus datos o llamarnos al <a href="tel:+34641450068" style="color:#547c24">641 45 00 68</a>.</p>
           </div>`
        : ''

      await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "CertificadoYa <info@certificadoya.es>",
          to: emailVal,
          subject: `🔐 Confirma tu email - CertificadoYa`,
          html: `
            <div style="font-family:Outfit,'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f7f2;padding:30px 15px">
              <div style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)">
                <div style="background:linear-gradient(135deg,#547c24,#3d5e1a);padding:30px 40px;text-align:center">
                  <div style="font-size:28px;font-weight:700;color:#fff">CertificadoYa</div>
                  <div style="font-size:13px;color:#b8d4a0;margin-top:4px">Confirma tu dirección de email</div>
                </div>
                <div style="padding:35px 40px 10px">
                  <div style="font-size:48px;text-align:center;margin-bottom:10px">🔐</div>
                  <h1 style="font-size:22px;font-weight:700;color:#1a1a1a;margin:0 0 6px;text-align:center">Casi listo, ${nombre}!</h1>
                  <p style="font-size:15px;color:#6b7b5e;line-height:1.5;text-align:center">Gracias por solicitar tu certificado energético. Para confirmar tu solicitud, haz clic en el botón de abajo.</p>
                </div>
                <div style="padding:10px 40px 20px;text-align:center">
                  <a href="${linkVerificacion}" style="display:inline-block;background:#547c24;color:#fff;text-decoration:none;padding:14px 32px;border-radius:10px;font-weight:700;font-size:16px">✅ Verificar mi email</a>
                  <p style="font-size:13px;color:#9aab8a;margin-top:12px">O copia este enlace en tu navegador:<br><span style="color:#6b7b5e;font-size:12px;word-break:break-all">${linkVerificacion}</span></p>
                </div>
                ${avisosEmail}
                <div style="padding:10px 40px 20px">
                  <div style="background:#f3f9eb;border-radius:8px;padding:16px 20px">
                    <p style="font-size:13px;color:#5a7a3a;margin:0 0 10px;font-weight:600">📋 Resumen de tu solicitud</p>
                    <table style="width:100%;border-collapse:collapse;font-size:13px">
                      <tr><td style="padding:4px 0;color:#6b7b5e">Nombre</td><td style="padding:4px 0;color:#1a1a1a;font-weight:600">${nombre}</td></tr>
                      <tr><td style="padding:4px 0;color:#6b7b5e">Teléfono</td><td style="padding:4px 0;color:#1a1a1a">${telefono || '⚠️ No proporcionado'}</td></tr>
                      <tr><td style="padding:4px 0;color:#6b7b5e">Zona</td><td style="padding:4px 0;color:#1a1a1a">${zonaVal || '—'} ${cpVal ? '(CP: ' + cpVal + ')' : '⚠️ Sin código postal'}</td></tr>
                      <tr><td style="padding:4px 0;color:#6b7b5e">Inmueble</td><td style="padding:4px 0;color:#1a1a1a">${m2Val || '—'} m² · ${tipoVal}</td></tr>
                    </table>
                  </div>
                </div>
                <div style="padding:0 40px 25px;text-align:center">
                  <p style="font-size:13px;color:#9aab8a;line-height:1.5">¿No has solicitado este servicio? Ignora este email.<br>Si tienes dudas, contáctanos en <a href="mailto:info@certificadoya.es" style="color:#547c24">info@certificadoya.es</a></p>
                  <p style="font-size:12px;color:#b8c4a8">Revisa también tu carpeta de spam si no ves este email.</p>
                </div>
                <div style="padding:20px 40px;text-align:center;font-size:12px;color:#9aab8a;border-top:1px solid #eef4e8">
                  <p style="margin:0 0 4px">CertificadoYa.es — Certificación energética en toda España</p>
                  <p style="margin:0"><a href="https://www.certificadoya.es/" style="color:#547c24">certificadoya.es</a> · <a href="mailto:info@certificadoya.es" style="color:#547c24">info@certificadoya.es</a></p>
                </div>
              </div>
            </div>
          `,
        }),
      }).catch(e => console.error("Error enviando email de verificación:", e));
    }

    // Construir respuesta con advertencias si faltan datos
    const respuesta: Record<string, any> = {
      success: true,
      leadId: data.id || data[0]?.id,
      necesitaVerificacion: !!emailVal,
      mensaje: emailVal
        ? 'Te hemos enviado un email de verificación. Revisa tu bandeja de entrada.'
        : 'Solicitud recibida. Te contactaremos pronto.'
    }

    if (avisosPre.length > 0) {
      respuesta.avisos = avisosPre
      respuesta.incompleto = true
      respuesta.mensaje += ' ' + (esCalculadora
        ? 'Recibirás un email con instrucciones para completar tus datos de contacto.'
        : 'Faltan algunos datos de contacto. Complétalos para que el técnico pueda contactarte.')
    }

    return new Response(JSON.stringify(respuesta), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
