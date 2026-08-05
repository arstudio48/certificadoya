import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST",
  "Access-Control-Allow-Headers": "Content-Type",
}

const STRIPE_WEBHOOK_SECRET = Deno.env.get("STRIPE_WEBHOOK_SECRET") ?? ""
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? ""
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""

// Función para verificar firma del webhook (HMAC-SHA256 estilo Stripe, Web Crypto)
async function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): Promise<boolean> {
  if (!signature || !secret) return false
  const parts = signature.split(",")
  let ts = ""
  let v1 = ""
  for (const p of parts) {
    const [k, v] = p.split("=")
    if (k === "t") ts = v
    if (k === "v1") v1 = v
  }
  if (!ts || !v1) return false
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  )
  const sigBuf = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(`${ts}.${payload}`)
  )
  const expected = Array.from(new Uint8Array(sigBuf))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
  if (expected.length !== v1.length) return false
  let diff = 0
  for (let i = 0; i < expected.length; i++) {
    diff |= expected.charCodeAt(i) ^ v1.charCodeAt(i)
  }
  return diff === 0
}

serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders })
  }

  try {
    const signature = req.headers.get("stripe-signature") ?? ""
    const body = await req.text()

    // Validar firma de Stripe
    if (!await verifyWebhookSignature(body, signature, STRIPE_WEBHOOK_SECRET)) {
      console.error("Firma de webhook inválida")
      return new Response(JSON.stringify({ error: "Firma inválida" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      })
    }

    const event = JSON.parse(body)
    console.log(`Evento Stripe recibido: ${event.type}`)

    // Procesar eventos relevantes
    if (
      event.type === "charge.succeeded" ||
      event.type === "payment_intent.succeeded"
    ) {
      const charge = event.data.object
      const metadata = charge.metadata || {}

      // Normalizar datos
      const nombre_cliente =
        metadata.nombre_cliente || charge.billing_details?.name || ""
      const email_cliente =
        metadata.email_cliente ||
        charge.billing_details?.email ||
        charge.receipt_email ||
        ""
      const telefono_cliente = metadata.telefono_cliente || ""
      const codigo_postal = metadata.codigo_postal || metadata.cp || ""
      const provincia = metadata.provincia || ""
      const tipo_inmueble = metadata.tipo_inmueble || "piso"
      const m2 = parseInt(metadata.m2) || 80
      const presupuesto_min = parseFloat(metadata.presupuesto_min) || 45
      const presupuesto_max = parseFloat(metadata.presupuesto_max) || 150

      // Validar datos requeridos
      if (!email_cliente || !telefono_cliente) {
        console.error(
          "Lead falta datos requeridos: email o teléfono",
          { email_cliente, telefono_cliente }
        )
        return new Response(
          JSON.stringify({
            error: "Lead incompleto: falta email o teléfono",
          }),
          {
            status: 400,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          }
        )
      }

      // Conectar a Supabase
      const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

      // Insertar lead en tabla `leads`
      const { data: newLead, error: insertError } = await supabase
        .from("leads")
        .insert({
          nombre_cliente,
          email_cliente,
          telefono_cliente,
          codigo_postal,
          provincia,
          tipo_inmueble,
          m2,
          presupuesto_min,
          presupuesto_max,
          fuente: "web-stripe",
          estado: "nuevo", // Auto-asignación se ejecutará en 30 min
          stripe_payment_intent: charge.id,
        })
        .select()

      if (insertError) {
        console.error("Error al insertar lead:", insertError)
        return new Response(JSON.stringify({ error: insertError.message }), {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        })
      }

      console.log(`Lead creado: ${newLead[0].id}`)

      // Disparar auto-asignación (llamar a función local o endpoint remoto)
      // NOTA: En producción, esto podría ser:
      // - Una llamada HTTP a un endpoint de auto_assign
      // - Un evento en una cola de tareas (Bull, RabbitMQ)
      // - Un cron job que se ejecute cada 30 minutos

      // Por ahora, simplemente registrar el evento
      const { error: auditError } = await supabase
        .from("audit_log")
        .insert({
          action: "stripe_webhook_received",
          entity: "leads",
          entity_id: newLead[0].id,
          details: {
            stripe_id: charge.id,
            amount: charge.amount / 100,
            customer: charge.customer,
          },
          created_at: new Date().toISOString(),
        })

      if (auditError) console.error("Error en audit:", auditError)

      return new Response(
        JSON.stringify({
          success: true,
          leadId: newLead[0].id,
          message: "Lead creado. Auto-asignación se ejecutará en 30 min.",
        }),
        {
          status: 200,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      )
    }

    // Otros eventos: ignorar
    return new Response(JSON.stringify({ success: true, ignored: true }), {
      status: 200,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    })
  } catch (err) {
    console.error("Error en webhook:", err)
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    })
  }
})
