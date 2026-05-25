import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

serve(async (req) => {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 })
  }

  try {
    const { nombre, email, telefono, titulacion } = await req.json()

    if (!nombre || !email || !telefono || !titulacion) {
      return new Response(JSON.stringify({ error: 'Faltan campos obligatorios' }), { status: 400 })
    }

    const supabase = createClient(supabaseUrl, supabaseKey)
    
    // Check if email already exists
    const { data: existing } = await supabase
      .from('tecnicos')
      .select('id')
      .eq('email', email)
      .maybeSingle()

    if (existing) {
      return new Response(JSON.stringify({ error: 'Este email ya está registrado' }), { status: 409 })
    }

    // Insert technician
    const { data, error } = await supabase
      .from('tecnicos')
      .insert({
        email,
        nombre,
        telefono,
        titulacion,
        verificado: false,
        activo: true
      })
      .select('id')
      .single()

    if (error) throw error

    // Generate magic link / registration token
    const token = crypto.randomUUID().replace(/-/g, '').slice(0, 24)

    return new Response(JSON.stringify({
      success: true,
      id: data.id,
      token: token,
      message: 'Registro completado. Completa tu perfil profesional.'
    }), {
      headers: { 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 })
  }
})
