// Edge Function temporal: ejecutar-sql
// SOLO USAR PARA MIGRACIONES — eliminar después
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.0?target=deno'

const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
const supabase = createClient(supabaseUrl, supabaseServiceKey)

serve(async (req) => {
  try {
    const { sql } = await req.json()
    if (!sql) return new Response(JSON.stringify({ error: 'sql requerido' }), { status: 400 })

    const { data, error } = await supabase.rpc('exec_sql', { query: sql })
    if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 })
    
    return new Response(JSON.stringify({ success: true, data }))
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500 })
  }
})
