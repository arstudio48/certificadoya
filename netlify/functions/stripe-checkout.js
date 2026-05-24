// Stripe Checkout Session — Netlify Function
// Crea una sesión de pago y devuelve la URL de Stripe
// Necesitas: STRIPE_SECRET_KEY en variables de entorno de Netlify

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// Precios por tipo de inmueble (piso, casa, local, nave)
const PRECIOS = {
  piso: { min: 45, max: 90 },
  casa: { min: 75, max: 150 },
  local: { min: 90, max: 200 },
  nave: { min: 120, max: 350 },
};

// CORS headers
const HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

exports.handler = async (event) => {
  // CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: HEADERS, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: HEADERS, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  try {
    const body = JSON.parse(event.body);
    const { nombre, email, telefono, cp, m2, tipo_inmueble, provincia } = body;

    // Validar
    if (!nombre || !email || !telefono || !cp || !m2) {
      return {
        statusCode: 400,
        headers: HEADERS,
        body: JSON.stringify({ error: 'Campos obligatorios faltantes' }),
      };
    }

    // Calcular precio
    const precios = PRECIOS[tipo_inmueble] || PRECIOS.piso;
    const precio = Math.round(m2 * 0.75); // Precio base estimado
    const precioFinal = Math.max(precios.min, Math.min(precios.max, precio));

    // Crear sesión Stripe
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      mode: 'payment',
      customer_email: email,
      line_items: [
        {
          price_data: {
            currency: 'eur',
            product_data: {
              name: `Certificado Energético - ${provincia || 'España'}`,
              description: `${m2} m² · ${tipo_inmueble} · CP ${cp}`,
              images: ['https://certificadoya.es/img/og-image.png'],
            },
            unit_amount: precioFinal * 100, // Stripe usa céntimos
          },
          quantity: 1,
        },
      ],
      metadata: {
        nombre_cliente: nombre,
        email_cliente: email,
        telefono_cliente: telefono,
        codigo_postal: cp,
        m2: String(m2),
        tipo_inmueble: tipo_inmueble || 'piso',
        provincia: provincia || '',
        precio_pagado: String(precioFinal),
      },
      success_url: `https://certificadoya.es/pago-exitoso.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `https://certificadoya.es/#presupuesto`,
    });

    return {
      statusCode: 200,
      headers: HEADERS,
      body: JSON.stringify({ url: session.url, session_id: session.id }),
    };
  } catch (error) {
    console.error('Stripe error:', error);
    return {
      statusCode: 500,
      headers: HEADERS,
      body: JSON.stringify({ error: 'Error al crear sesión de pago' }),
    };
  }
};
