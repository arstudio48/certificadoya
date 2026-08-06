// Edge Function temporal: consultar saldo Stripe
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const stripeKey = Deno.env.get("STRIPE_SECRET_KEY") || "";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const resp = await fetch("https://api.stripe.com/v1/balance", {
      headers: { Authorization: `Bearer ${stripeKey}` },
    });
    const data = await resp.json();
    return new Response(JSON.stringify(data, null, 2), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
