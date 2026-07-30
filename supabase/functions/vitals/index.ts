import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

serve(async (req) => {
  if (req.method !== 'POST') return new Response('Method not allowed', { status: 405 })
  
  try {
    const vital = await req.json()
    
    const { error } = await supabase.from('web_vitals').insert({
      metric_name: vital.name,
      value: vital.value,
      rating: vital.rating,
      delta: vital.delta,
      metric_id: vital.id,
      url: vital.url,
      referrer: vital.referrer,
      received_at: new Date(vital.timestamp || Date.now()).toISOString()
    })
    
    if (error) throw error
    return new Response('OK', { status: 200 })
  } catch (e) {
    console.error('Vitals error:', e)
    return new Response('Error', { status: 500 })
  }
})
