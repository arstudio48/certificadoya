import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST",
  "Access-Control-Allow-Headers": "Content-Type",
}

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? ""
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? ""

const emailTemplates = {
  nuevo: (cliente) => ({
    subject: "Tu solicitud de certificado energético fue recibida",
    html: `
      <h2>¡Hola ${cliente.nombre_cliente}!</h2>
      <p>Hemos recibido tu solicitud de certificado energético.</p>
      <p><strong>Próximos pasos:</strong></p>
      <ul>
        <li>En <strong>24 horas</strong> te confirmaremos el técnico asignado</li>
        <li>El técnico te llamará para fijar la visita</li>
        <li>Certificado listo en <strong>48-96 horas</strong></li>
      </ul>
      <p>¿Preguntas? Contacta a <strong>641 45 00 68</strong></p>
    `,
  }),

  asignado: (cliente, tecnico) => ({
    subject: `✅ Técnico confirmado: ${tecnico.nombre}`,
    html: `
      <h2>¡Tu técnico ha sido confirmado!</h2>
      <p>Detalles de tu técnico certificador:</p>
      <ul>
        <li><strong>Nombre:</strong> ${tecnico.nombre}</li>
        <li><strong>Teléfono:</strong> ${tecnico.telefono}</li>
        <li><strong>Email:</strong> ${tecnico.email}</li>
      </ul>
      <p>El técnico <strong>te llamará en las próximas 24 horas</strong> para programar la visita.</p>
      <p>Si no recibes llamada, contacta a <strong>641 45 00 68</strong></p>
    `,
  }),

  aceptado: (cliente, tecnico) => ({
    subject: "Tu encargo ha sido aceptado",
    html: `
      <h2>✅ El técnico ${tecnico.nombre} aceptó tu encargo</h2>
      <p>La visita se programará en <strong>24-48 horas</strong>.</p>
      <p>El técnico completará el certificado en <strong>2-7 días</strong> después de la visita.</p>
      <p>Estaremos en contacto para actualizarte del progreso.</p>
    `,
  }),

  rechazado: (cliente) => ({
    subject: "Buscando otro técnico para tu encargo",
    html: `
      <h2>Otros técnicos están revisando tu encargo</h2>
      <p>El primer técnico asignado no pudo aceptar tu solicitud.</p>
      <p><strong>Buenas noticias:</strong> Ya estamos buscando otro técnico disponible en tu zona.</p>
      <p>Te contactaremos en máximo <strong>24 horas</strong> con un nuevo técnico.</p>
    `,
  }),

  registrado: (cliente, certificado) => ({
    subject: "🎉 Tu certificado energético está listo",
    html: `
      <h2>¡Tu certificado está listo y registrado!</h2>
      <p><strong>Detalles del certificado:</strong></p>
      <ul>
        <li><strong>Calificación:</strong> ${certificado.calificacion}</li>
        <li><strong>Número de registro:</strong> ${certificado.numero_registro}</li>
        <li><strong>Válido hasta:</strong> ${certificado.fecha_vencimiento}</li>
      </ul>
      <p><a href="${certificado.pdf_url}" style="background: #16a34a; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📥 Descargar Certificado</a></p>
      <p>El certificado está <strong>registrado oficialmente</strong> en la CCAA de ${cliente.provincia}.</p>
    `,
  }),

  completado: (cliente) => ({
    subject: "Transacción completada",
    html: `
      <h2>✅ Tu solicitud de certificado ha sido completada</h2>
      <p>Gracias por usar CertificadoYa. Tu certificado energético está <strong>completamente registrado y válido</strong>.</p>
      <p>¿Necesitas ayuda? Contacta a <strong>info@certificadoya.es</strong> o <strong>641 45 00 68</strong></p>
    `,
  }),
}

async function sendEmailViaResend(
  to: string,
  subject: string,
  html: string
): Promise<boolean> {
  try {
    const response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${RESEND_API_KEY}`,
      },
      body: JSON.stringify({
        from: "notificaciones@certificadoya.es",
        to,
        subject,
        html,
      }),
    })

    const data = await response.json()
    return response.ok && data.id
  } catch (err) {
    console.error("Error enviando email Resend:", err)
    return false
  }
}

serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders })
  }

  try {
    const { lead, tecnico, certificado, estado } = await req.json()

    if (!lead || !estado) {
      return new Response(
        JSON.stringify({ error: "Faltan lead o estado" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      )
    }

    // Obtener template
    const template =
      emailTemplates[estado as keyof typeof emailTemplates]
    if (!template) {
      console.error(`Template no encontrado: ${estado}`)
      return new Response(
        JSON.stringify({ error: `Template ${estado} no existe` }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      )
    }

    // Generar email
    const emailContent =
      estado === "asignado"
        ? template(lead, tecnico)
        : estado === "aceptado"
          ? template(lead, tecnico)
          : estado === "registrado"
            ? template(lead, certificado)
            : template(lead)

    // Enviar email
    const success = await sendEmailViaResend(
      lead.email_cliente,
      emailContent.subject,
      emailContent.html
    )

    if (!success) {
      console.error(`Fallo al enviar email a ${lead.email_cliente}`)
    }

    // Conectar a Supabase y registrar en auditoría
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    await supabase.from("notificaciones").insert({
      lead_id: lead.id,
      email_dest: lead.email_cliente,
      estado_trigger: estado,
      asunto: emailContent.subject,
      body_html: emailContent.html,
      enviado_at: new Date().toISOString(),
      success,
    })

    return new Response(
      JSON.stringify({
        success,
        message: success
          ? "Email enviado"
          : "Email no se pudo enviar (ver logs)",
      }),
      {
        status: success ? 200 : 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    )
  } catch (err) {
    console.error("Error en notify-client:", err)
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    })
  }
})
