// Registro de técnico — Netlify Function
// Recibe datos del formulario, los valida y guarda en Supabase
// Usa SUPABASE_SERVICE_KEY (no la anon key del frontend) — seguro
const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co';

const HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: HEADERS, body: '' };
  }
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: HEADERS, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  if (!process.env.SUPABASE_SERVICE_KEY) {
    console.error('SUPABASE_SERVICE_KEY not set in env');
    return { statusCode: 500, headers: HEADERS, body: JSON.stringify({ error: 'Config error' }) };
  }

  try {
    const body = JSON.parse(event.body);
    const { nombre, email, telefono, titulacion } = body;

    // Validar campos obligatorios
    if (!nombre || !email || !telefono || !titulacion) {
      return { statusCode: 400, headers: HEADERS, body: JSON.stringify({ error: 'Todos los campos obligatorios' }) };
    }

    // Validar email
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return { statusCode: 400, headers: HEADERS, body: JSON.stringify({ error: 'Email inválido' }) };
    }

    // Validar teléfono español
    const tlf = telefono.replace(/\s/g, '');
    if (!/^\d{9}$/.test(tlf)) {
      return { statusCode: 400, headers: HEADERS, body: JSON.stringify({ error: 'Teléfono inválido (9 dígitos)' }) };
    }

    const supabase = createClient(SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

    // Verificar si ya existe
    const { data: existente } = await supabase
      .from('tecnicos')
      .select('email')
      .eq('email', email)
      .maybeSingle();

    if (existente) {
      return { statusCode: 409, headers: HEADERS, body: JSON.stringify({ error: 'Este email ya está registrado' }) };
    }

    // Insertar técnico
    const { data, error } = await supabase
      .from('tecnicos')
      .insert([{
        email,
        nombre,
        telefono: tlf,
        titulacion,
        step: 1, // Paso 1 completado, falta step 2 (perfil)
        verificado: false,
        activo: false
      }])
      .select()
      .single();

    if (error) {
      console.error('Supabase insert error:', error);
      return { statusCode: 500, headers: HEADERS, body: JSON.stringify({ error: 'Error al registrar' }) };
    }

    console.log(`✅ Técnico registrado: ${email}`);

    return {
      statusCode: 200,
      headers: HEADERS,
      body: JSON.stringify({
        ok: true,
        message: 'Registro completado. Te enviaremos un email para activar tu cuenta.',
        email: email
      })
    };
  } catch (err) {
    console.error('Error:', err);
    return { statusCode: 500, headers: HEADERS, body: JSON.stringify({ error: 'Error interno' }) };
  }
};
