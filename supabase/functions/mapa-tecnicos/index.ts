import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })
  if (req.method !== 'GET') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }

  const supabase = createClient(supabaseUrl, supabaseKey)

  // Dueño de la plataforma: NUNCA recibe encargos (excluido del pool de asignación).
  // Se descuenta del mapa para que los círculos reflejen técnicos REALMENTE asignables.
  const EXCLUIR_DUENO = '4b805c7b-0bbf-490d-8000-21c620cbf30f'

  try {
      // Solo agregados: provincia + recuento de técnicos activos y verificados,
      // EXCLUYENDO al dueño. NO se exponen emails, teléfonos ni datos personales.
      const { data, error } = await supabase
        .from('tecnicos')
        .select('id, provincia')
        .eq('activo', true)
        .eq('verificado', true)
        .neq('id', EXCLUIR_DUENO)

    if (error) throw error

    // Contar por provincia. La provincia puede ser NULL, lista separada por comas
    // (p.ej. "Huesca,Teruel,Zaragoza") o valor único. Se normaliza:
    // - NULL/vacío -> "SIN DEFINIR" (no recibe leads)
    // - lista -> se cuenta en cada provincia de la lista
    const counts: Record<string, number> = {}
    for (const t of data || []) {
      const p = (t.provincia || '').trim()
      if (!p) {
        counts['SIN DEFINIR'] = (counts['SIN DEFINIR'] || 0) + 1
        continue
      }
      const parts = p.split(',').map((s) => s.trim()).filter(Boolean)
      for (const part of parts) {
        counts[part] = (counts[part] || 0) + 1
      }
    }

    const provincias = Object.entries(counts)
      .map(([provincia, n]) => ({ provincia, n }))
      .sort((a, b) => b.n - a.n)

    return new Response(
      JSON.stringify({ success: true, total: (data || []).length, provincias }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } },
    )
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})
