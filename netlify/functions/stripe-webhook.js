// Stripe Webhook — Netlify Function
// Escucha eventos de Stripe (checkout.session.completed)
// Guarda el lead en Supabase como "pagado"
// Necesitas: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, SUPABASE_SERVICE_KEY en env vars

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co';

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  // Verificar firma del webhook
  let sig = event.headers['stripe-signature'];
  let stripeEvent;
  
  try {
    stripeEvent = stripe.webhooks.constructEvent(
      event.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return { statusCode: 400, body: JSON.stringify({ error: 'Invalid signature' }) };
  }

  // Solo nos interesa checkout completado
  if (stripeEvent.type === 'checkout.session.completed') {
    const session = stripeEvent.data.object;
    const meta = session.metadata;

    // Guardar en Supabase
    try {
      const supabase = createClient(SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);
      
      const { error } = await supabase.from('leads').insert([{
        nombre_cliente: meta.nombre_cliente,
        email_cliente: meta.email_cliente,
        telefono_cliente: meta.telefono_cliente,
        codigo_postal: meta.codigo_postal,
        zona: meta.provincia || '',
        m2: parseInt(meta.m2),
        tipo_inmueble: meta.tipo_inmueble,
        presupuesto_min: parseInt(meta.precio_pagado),
        presupuesto_max: parseInt(meta.precio_pagado),
        estado: 'pagado',
        stripe_session_id: session.id,
        stripe_payment_intent: session.payment_intent,
        monto_pagado: session.amount_total / 100,
        moneda: session.currency,
        fuente: 'web_stripe'
      }]);

      if (error) {
        console.error('Supabase insert error:', error);
        return { statusCode: 500, body: JSON.stringify({ error: 'Database error' }) };
      }

      console.log(`✅ Lead creado de ${meta.email_cliente} - Pagado ${session.amount_total / 100}€`);
    } catch (err) {
      console.error('Supabase error:', err);
      return { statusCode: 500, body: JSON.stringify({ error: 'Database error' }) };
    }
  }

  return { statusCode: 200, body: JSON.stringify({ received: true }) };
};
