// Stripe integration for CertificadoYa
// Client-side: create payment intent for lead payment
// Server-side: handle payment confirmation

const STRIPE_PUBLISHABLE_KEY = 'pk_live_...'; // Replace with your Stripe publishable key
const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co';
const SUPABASE_KEY = 'sb_publishable_MsDx5jVGtDAzoB3l3-8DiQ_BxWpChA0';

let stripe;
let elements;

async function initStripe() {
  if (!window.Stripe) {
    const script = document.createElement('script');
    script.src = 'https://js.stripe.com/v3/';
    script.onload = () => {
      stripe = Stripe(STRIPE_PUBLISHABLE_KEY);
    };
    document.head.appendChild(script);
  } else {
    stripe = Stripe(STRIPE_PUBLISHABLE_KEY);
  }
}

// Lead payment flow
async function pagarLead(leadData) {
  // leadData: { nombre, telefono, email, cp, m2, tipo, provincia, precioMin, precioMax }
  try {
    // 1. Call the Netlify/Edge function to create payment intent
    const response = await fetch('/api/create-payment-intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        amount: Math.round((leadData.precioMin + leadData.precioMax) / 2), // precio medio
        currency: 'eur',
        metadata: {
          tipo: 'lead-cee',
          nombre_cliente: leadData.nombre,
          telefono_cliente: leadData.telefono,
          email_cliente: leadData.email || '',
          codigo_postal: leadData.cp,
          m2: leadData.m2.toString(),
          tipo_inmueble: leadData.tipo,
          provincia: leadData.provincia
        }
      })
    });

    const { clientSecret, error } = await response.json();
    if (error) throw new Error(error);

    // 2. Confirm payment with Stripe
    const { paymentIntent, error: confirmError } = await stripe.confirmCardPayment(clientSecret);
    if (confirmError) throw new Error(confirmError.message);

    // 3. Save lead to Supabase after successful payment
    const { createClient } = await import('https://esm.sh/@supabase/supabase-js@2');
    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
    await supabase.from('leads').insert([{
      nombre_cliente: leadData.nombre,
      telefono_cliente: leadData.telefono,
      email_cliente: leadData.email || null,
      codigo_postal: leadData.cp,
      m2: parseInt(leadData.m2),
      tipo_inmueble: leadData.tipo,
      presupuesto_min: leadData.precioMin,
      presupuesto_max: leadData.precioMax,
      provincia: leadData.provincia,
      estado: 'pagado',
      stripe_payment_id: paymentIntent.id,
      stripe_amount: paymentIntent.amount / 100,
      fuente: 'web'
    }]);

    return { success: true, paymentIntent };
  } catch (e) {
    console.error('Payment error:', e);
    return { success: false, error: e.message };
  }
}

// Técnico subscription flow (Plan Mensual)
async function crearSuscripcionTecnico(tecnicoData) {
  // tecnicoData: { nombre, email, plan: 'mensual'|'por-lead' }
  try {
    const response = await fetch('/api/create-subscription', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: tecnicoData.email,
        nombre: tecnicoData.nombre,
        plan: tecnicoData.plan
      })
    });

    const { subscriptionId, clientSecret } = await response.json();

    // Confirm subscription payment (Stripe Checkout or Payment Element)
    const { error } = await stripe.confirmSetup({
      elements: stripe.elements(),
      confirmParams: {
        return_url: window.location.origin + '/panel-tecnicos.html?suscrito=true'
      }
    });

    if (error) throw new Error(error.message);
    return { success: true, subscriptionId };
  } catch (e) {
    console.error('Subscription error:', e);
    return { success: false, error: e.message };
  }
}
