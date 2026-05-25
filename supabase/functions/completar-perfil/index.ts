import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

serve(async (req) => {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 })
  }

  try {
    const { token, email, titulacion, colegiado, colegio, provincias, iban, plan } = await req.json()

    if (!token || !email || !titulacion || !colegiado || !colegio || !provincias) {
      return new Response(JSON.stringify({ error: 'Faltan campos obligatorios' }), { status: 400 })
    }

    const supabase = createClient(supabaseUrl, supabaseKey)

    // Buscar al técnico por email y token
    const { data: tecnico, error: searchError } = await supabase
      .from('tecnicos')
      .select('id')
      .eq('email', email)
      .eq('token', token)
      .single()

    if (searchError || !tecnico) {
      return new Response(JSON.stringify({ error: 'Token o email inválido' }), { status: 401 })
    }

    // Actualizar perfil completo
    const provinciaStr = Array.isArray(provincias) ? provincias.join(',') : provincias
    const { error: updateError } = await supabase
      .from('tecnicos')
      .update({
        titulacion,
        numero_colegiado: colegiado,
        provincia: provinciaStr,
        iban: iban || null,
        plan: plan || 'por-lead',
        verificado: false,
        token: null // Limpiar token (ya usado)
      })
      .eq('id', tecnico.id)

    if (updateError) throw updateError

    return new Response(JSON.stringify({
      success: true,
      message: 'Perfil completado correctamente. Tu solicitud está pendiente de verificación.'
    }), {
      headers: { 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 })
  }
})
