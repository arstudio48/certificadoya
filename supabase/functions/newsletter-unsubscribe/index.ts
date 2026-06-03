import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co'

function htmlFormulario(email: string, error?: string, success?: string): string {
  const opciones = [
    { value: 'no_interesa', label: 'Ya no me interesa' },
    { value: 'demasiados', label: 'Recibo demasiados correos' },
    { value: 'no_solicitado', label: 'No solicité esta suscripción' },
    { value: 'contenido', label: 'El contenido no es relevante para mí' },
    { value: 'otro', label: 'Otro motivo' },
  ]

  const opcionesHtml = opciones.map(o =>
    `<label class="radio-label">
       <input type="radio" name="reason" value="${o.value}" required>
       <span>${o.label}</span>
     </label>`
  ).join('\n')

  const alerta = error
    ? `<div class="alerta error">${error}</div>`
    : success
    ? `<div class="alerta success">${success}</div>`
    : ''

  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Desuscribirse — CertificadoYa</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', Arial, sans-serif;
      background: #f0f2eb;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 20px;
    }
    .card {
      background: #fff;
      border-radius: 16px;
      max-width: 480px;
      width: 100%;
      overflow: hidden;
      box-shadow: 0 2px 20px rgba(0,0,0,.08);
    }
    .header {
      background: linear-gradient(135deg, #547c24, #3d5e1a);
      padding: 28px 32px;
      text-align: center;
    }
    .header h1 {
      font-size: 22px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 4px;
    }
    .header p {
      font-size: 13px;
      color: #b8d4a0;
    }
    .body {
      padding: 28px 32px 20px;
    }
    .body h2 {
      font-size: 17px;
      font-weight: 600;
      color: #1a1a1a;
      margin-bottom: 6px;
    }
    .body p {
      font-size: 14px;
      color: #6b7b5e;
      margin-bottom: 18px;
      line-height: 1.5;
    }
    .email-display {
      background: #f5f7f2;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 14px;
      color: #3d5e1a;
      font-weight: 600;
      text-align: center;
      margin-bottom: 18px;
      word-break: break-all;
    }
    .alerta {
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 13px;
      margin-bottom: 14px;
    }
    .alerta.error {
      background: #fef2f2;
      color: #b91c1c;
      border: 1px solid #fecaca;
    }
    .alerta.success {
      background: #f0fdf4;
      color: #166534;
      border: 1px solid #bbf7d0;
    }
    .radio-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-bottom: 18px;
    }
    .radio-label {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border: 1px solid #e0e6d8;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      color: #2d3a1f;
      transition: all .15s;
    }
    .radio-label:hover {
      border-color: #547c24;
      background: #f9fbf5;
    }
    .radio-label input:checked + span {
      color: #3d5e1a;
      font-weight: 600;
    }
    .radio-label input:checked {
      accent-color: #547c24;
    }
    .radio-label:has(input:checked) {
      border-color: #547c24;
      background: #f0f6e8;
    }
    .radio-label input[type="radio"] {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
    }
    .texto-motivo {
      display: none;
      margin-top: -10px;
      margin-bottom: 18px;
    }
    .texto-motivo.visible {
      display: block;
    }
    .texto-motivo textarea {
      width: 100%;
      padding: 10px 14px;
      border: 1px solid #e0e6d8;
      border-radius: 8px;
      font-size: 13px;
      font-family: inherit;
      resize: vertical;
      min-height: 60px;
      color: #2d3a1f;
    }
    .texto-motivo textarea:focus {
      outline: none;
      border-color: #547c24;
      box-shadow: 0 0 0 3px rgba(84,124,36,.12);
    }
    .btn-submit {
      width: 100%;
      padding: 12px;
      background: #547c24;
      color: #fff;
      border: none;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: background .15s;
    }
    .btn-submit:hover {
      background: #3d5e1a;
    }
    .btn-submit:disabled {
      background: #b8c8a9;
      cursor: not-allowed;
    }
    .footer {
      padding: 16px 32px 24px;
      text-align: center;
      font-size: 12px;
      color: #9aab8a;
      border-top: 1px solid #eef4e8;
    }
    .footer a {
      color: #547c24;
      text-decoration: none;
    }
    .oculto {
      display: none;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h1>CertificadoYa</h1>
      <p>Gestiona tu suscripción</p>
    </div>
    <div class="body">
      ${success ? `
        <h2>✅ Todo listo</h2>
        <p>Te has dado de baja correctamente. Ya no recibirás más correos nuestros.</p>
        <p style="margin-top:12px;font-size:13px;color:#9aab8a">Si fue un error, puedes volver a suscribirte desde <a href="https://www.certificadoya.es/" style="color:#547c24">certificadoya.es</a></p>
      ` : `
        <h2>¿Nos dejas?</h2>
        <p>Lamentamos que te vayas. Cuéntanos brevemente el motivo para mejorar:</p>
        ${email ? `<div class="email-display">${email}</div>` : ''}
        ${alerta}
        <form id="formulario-baja" onsubmit="enviarBaja(event)">
          <input type="hidden" name="email" value="${email}">
          <div class="radio-group">
            ${opcionesHtml}
          </div>
          <div class="texto-motivo" id="texto-motivo">
            <textarea name="reason_text" placeholder="Cuéntanos más (opcional)..." rows="3"></textarea>
          </div>
          <button type="submit" class="btn-submit" id="btn-submit">Darme de baja</button>
        </form>
      `}
    </div>
    <div class="footer">
      <a href="https://www.certificadoya.es/">certificadoya.es</a> · Certificado de Eficiencia Energética
    </div>
  </div>
  <script>
    // Mostrar textarea cuando se selecciona "Otro motivo"
    document.querySelectorAll('input[name="reason"]').forEach(r => {
      r.addEventListener('change', () => {
        const textarea = document.getElementById('texto-motivo');
        if (r.value === 'otro') {
          textarea.classList.add('visible');
        } else {
          textarea.classList.remove('visible');
        }
      });
    });

    async function enviarBaja(event) {
      event.preventDefault();
      const form = event.target;
      const btn = document.getElementById('btn-submit');
      const formData = new FormData(form);
      const data = {
        email: formData.get('email'),
        reason: formData.get('reason'),
        reason_text: formData.get('reason_text') || ''
      };

      if (!data.email) {
        alert('Falta el email. Por favor, introdúcelo manualmente.');
        return;
      }

      btn.disabled = true;
      btn.textContent = 'Procesando...';

      try {
        const resp = await fetch('${SUPABASE_URL}/functions/v1/newsletter-unsubscribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        const result = await resp.json();
        if (result.success) {
          document.querySelector('.body').innerHTML = \`
            <h2>✅ Todo listo</h2>
            <p>Te has dado de baja correctamente. Ya no recibirás más correos nuestros.</p>
            <p style="margin-top:12px;font-size:13px;color:#9aab8a">Si fue un error, puedes volver a suscribirte desde <a href="https://www.certificadoya.es/" style="color:#547c24">certificadoya.es</a></p>
          \`;
        } else {
          alert('Error: ' + (result.error || 'No se pudo procesar la baja'));
          btn.disabled = false;
          btn.textContent = 'Darme de baja';
        }
      } catch(e) {
        alert('Error de conexión. Inténtalo de nuevo.');
        btn.disabled = false;
        btn.textContent = 'Darme de baja';
      }
    }
  </script>
</body>
</html>`
}

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  const token = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
  if (!token) {
    return new Response(JSON.stringify({ error: 'Error de configuración del servidor' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }

  // GET — mostrar formulario
  if (req.method === 'GET') {
    const url = new URL(req.url)
    const email = (url.searchParams.get('email') || '').trim().toLowerCase()
    const html = htmlFormulario(email)
    return new Response(html, {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'text/html; charset=utf-8' }
    })
  }

  // POST — procesar baja
  if (req.method === 'POST') {
    try {
      const body = await req.json()
      const email = (body.email || '').trim().toLowerCase()
      const reason = body.reason || ''
      const reasonText = body.reason_text || ''

      if (!email) {
        return new Response(JSON.stringify({ error: 'Email requerido' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        return new Response(JSON.stringify({ error: 'Email inválido' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // Actualizar suscriptor: marcar como inactivo y guardar motivo
      const updateRes = await fetch(
        `${SUPABASE_URL}/rest/v1/newsletter_subscribers?email=eq.${encodeURIComponent(email)}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'apikey': token,
            'Authorization': `Bearer ${token}`,
            'Prefer': 'return=representation'
          },
          body: JSON.stringify({
            active: false,
            unsubscribe_reason: reason === 'otro' && reasonText
              ? `otro: ${reasonText}`
              : reason
          })
        }
      )

      if (!updateRes.ok) {
        const errText = await updateRes.text()
        console.error('Error actualizando suscriptor:', errText)
        return new Response(JSON.stringify({ error: 'No se encontró esa suscripción' }), {
          status: 404,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const updated = await updateRes.json()
      const found = Array.isArray(updated) ? updated.length > 0 : !!updated

      return new Response(JSON.stringify({
        success: true,
        message: 'Te has dado de baja correctamente'
      }), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })

    } catch (err) {
      console.error('Error en newsletter-unsubscribe POST:', err)
      return new Response(JSON.stringify({ error: 'Error interno del servidor' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
  }

  return new Response(JSON.stringify({ error: 'Método no permitido' }), {
    status: 405,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  })
})
