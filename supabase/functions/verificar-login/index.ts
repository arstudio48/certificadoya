import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers: corsHeaders })
  }

  try {
    const { email, codigo } = await req.json()

    if (!email || !codigo) {
      return new Response(JSON.stringify({ error: 'Email y código requeridos' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    const supabase = createClient(supabaseUrl, supabaseKey)

    // Verificar código
    const { data: tecnico, error: findError } = await supabase
      .from('tecnicos')
      .select('id, nombre, email, provincia, telefono, titulacion, verificado, activo, token')
      .eq('email', email)
      .eq('activo', true)
      .maybeSingle()

    if (findError || !tecnico) {
      return new Response(JSON.stringify({ error: 'Técnico no encontrado' }), { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    if (tecnico.token !== codigo) {
      return new Response(JSON.stringify({ error: 'Código incorrecto' }), { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // Generar token de sesión (válido 7 días)
    const sessionToken = crypto.randomUUID().replace(/-/g, '').slice(0, 32)
    const sessionExpira = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()

    // Limpiar código OTP y guardar token de sesión
    await supabase
      .from('tecnicos')
      .update({
        token: sessionToken,
        updated_at: new Date().toISOString()
      })
      .eq('id', tecnico.id)

    // Obtener provincias desde el perfil del técnico
    const provincias = tecnico.provincia ? tecnico.provincia.split(',').map(p => p.trim().toLowerCase()) : []

    return new Response(JSON.stringify({
      success: true,
      sessionToken,
      tecnico: {
        id: tecnico.id,
        nombre: tecnico.nombre,
        email: tecnico.email,
        provincias,
        verificado: tecnico.verificado
      }
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
