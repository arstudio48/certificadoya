// 📌 DEPRECATED / DEAD CODE — Este archivo NO se carga en ninguna página HTML.
// La integración de pagos se maneja desde js/main.js mediante Supabase Edge Functions.
// 
// Eliminar cuando se confirme que ningún flujo depende de esto.
// 
// Los pagos reales se gestionan vía:
//   - EDGE_FUNCTION_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co/functions/v1/solicitar-servicio'
//   - stripe-checkout Edge Function
//
// (= ^ ( . . )^) ✧  Aquí descansan los sueños de un Stripe directo al frontend.

const STRIPE_PUBLISHABLE_KEY = 'pk_live_...'; // ← placeholder, no válida
const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co';
const SUPABASE_KEY = 'sb_publishable_MsDx5jVGtDAzoB3l3-8DiQ_BxWpChA0';
