import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co'
  const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')

  if (!serviceKey) {
    return new Response(JSON.stringify({ error: 'No service key' }), { status: 500, headers: corsHeaders })
  }

  try {
    // Ejecutar migración vía REST API directo a postgres
    const sql = `
      ALTER TABLE leads ADD COLUMN IF NOT EXISTS email_verificado BOOLEAN DEFAULT false;
      ALTER TABLE leads ADD COLUMN IF NOT EXISTS token_verificacion TEXT DEFAULT null;
      ALTER TABLE leads ADD COLUMN IF NOT EXISTS email_verificado_en TIMESTAMPTZ DEFAULT null;
    `

    const res = await fetch(`${SUPABASE_URL}/rest/v1/rpc/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': serviceKey,
        'Authorization': `Bearer ${serviceKey}`,
        'X-SQL': sql
      },
      body: JSON.stringify({})
    })

    const text = await res.text()
    return new Response(JSON.stringify({ status: res.status, body: text }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    return new Response(JSON.stringify({ error: msg }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
