// Cloudflare Worker para registro de tecnicos CertificadoYa
// Endpoint: POST /api/registro-tecnico

export default {
  async fetch(request, env) {
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ok: false, error: 'Method not allowed'}), {status: 405});
    }

    try {
      const body = await request.json();
      const t = body.tecnico;

      if (!t.nombre || !t.email || !t.profesion || !t.colegiado || !t.provincias) {
        return new Response(JSON.stringify({ok: false, error: 'Faltan campos obligatorios'}), {status: 400});
      }

      // Guardar en KV
      const id = crypto.randomUUID().slice(0, 8);
      const registro = {
        id,
        fecha: new Date().toISOString(),
        nombre: t.nombre,
        email: t.email,
        telefono: t.telefono || '',
        profesion: t.profesion,
        colegiado: t.colegiado,
        provincias: t.provincias,
        web: t.web || '',
        estado: 'pendiente'
      };
      await env.TECNICOS_KV.put(id, JSON.stringify(registro));

      // Generar slug para el perfil
      const slug = t.nombre.toLowerCase()
        .replace(/[áàäâ]/g, 'a').replace(/[éèëê]/g, 'e').replace(/[íìïî]/g, 'i')
        .replace(/[óòöô]/g, 'o').replace(/[úùüû]/g, 'u').replace(/ñ/g, 'n')
        .replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
      const perfilUrl = `https://www.certificadoya.es/tecnicos/${slug}/`;

      // Email HTML de bienvenida
      const emailHtml = `<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#f5f7f2;font-family:'Outfit','Segoe UI',Arial,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7f2">
    <tr><td align="center" style="padding:30px 15px">
      <table width="600" style="max-width:100%;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)">
        <tr>
          <td style="background:linear-gradient(135deg,#547c24,#3d5e1a);padding:30px 40px;text-align:center">
            <div style="font-size:28px;font-weight:700;color:#ffffff;letter-spacing:-.5px">CertificadoYa</div>
            <div style="font-size:13px;color:#b8d4a0;margin-top:4px">Certificado de Eficiencia Energética</div>
          </td>
        </tr>
        <tr>
          <td style="padding:35px 40px 10px 40px">
            <h1 style="font-size:22px;font-weight:700;color:#1a1a1a;margin:0 0 6px 0">¡Bienvenido a CertificadoYa, ${t.nombre}!</h1>
            <p style="font-size:15px;color:#6b7b5e;line-height:1.5;margin:0">Gracias por unirte a nuestra red de técnicos certificadores. Ya estamos revisando tu solicitud.</p>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 40px">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8faf5;border-radius:12px;padding:20px">
              <tr><td style="padding:0 0 12px 0"><div style="font-size:13px;font-weight:600;color:#547c24;text-transform:uppercase;letter-spacing:.5px">Tu perfil publico</div></td></tr>
              <tr><td style="padding:0 0 16px 0"><p style="font-size:14px;color:#4a5a3a;line-height:1.5;margin:0">Cuando verifiquemos tus datos, tu perfil estara disponible en:</p></td></tr>
              <tr><td style="padding:0 0 5px 0"><a href="${perfilUrl}" style="display:inline-block;padding:10px 20px;background:#547c24;color:#ffffff;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none">Ver mi perfil</a></td></tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:10px 40px">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f5ea;border:2px dashed #b8d4a0;border-radius:12px;padding:20px">
              <tr><td style="padding:0 0 10px 0"><div style="font-size:13px;font-weight:600;color:#3d5e1a">Comparte tu perfil en tu web</div></td></tr>
              <tr><td style="padding:0 0 14px 0"><p style="font-size:13px;color:#4a5a3a;line-height:1.5;margin:0">Si tienes web, copia y pega este codigo donde quieras mostrar tu colaboracion:<br><br>
                <code style="display:block;background:#ffffff;padding:12px;border-radius:8px;font-size:12px;color:#333;word-break:break-all;border:1px solid #dce8d0">&lt;a href="${perfilUrl}" target="_blank"&gt;Colaboro con CertificadoYa&lt;/a&gt;</code>
              </p></td></tr>
              <tr><td><p style="font-size:12px;color:#9aab8a;margin:0">Esto ayuda a que mas clientes te encuentren.</p></td></tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:25px 40px 10px 40px">
            <h2 style="font-size:16px;font-weight:600;color:#1a1a1a;margin:0 0 14px 0">Que sigue ahora?</h2>
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td width="50%" style="padding:0 8px 12px 0;vertical-align:top">
                  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8faf5;border-radius:10px;padding:14px">
                    <tr><td style="font-size:18px;padding:0 0 4px 0">Verificacion</td></tr>
                    <tr><td style="font-size:12px;color:#6b7b5e;line-height:1.4">Revisamos tu colegiacion en 24-48h</td></tr>
                  </table>
                </td>
                <td width="50%" style="padding:0 0 12px 8px;vertical-align:top">
                  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8faf5;border-radius:10px;padding:14px">
                    <tr><td style="font-size:18px;padding:0 0 4px 0">Leads</td></tr>
                    <tr><td style="font-size:12px;color:#6b7b5e;line-height:1.4">Recibiras clientes de tu zona</td></tr>
                  </table>
                </td>
              </tr>
              <tr>
                <td width="50%" style="padding:0 8px 0 0;vertical-align:top">
                  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8faf5;border-radius:10px;padding:14px">
                    <tr><td style="font-size:18px;padding:0 0 4px 0">Sin cuotas</td></tr>
                    <tr><td style="font-size:12px;color:#6b7b5e;line-height:1.4">Tu pones tus tarifas. Pagas solo por lead</td></tr>
                  </table>
                </td>
                <td width="50%" style="padding:0 0 0 8px;vertical-align:top">
                  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8faf5;border-radius:10px;padding:14px">
                    <tr><td style="font-size:18px;padding:0 0 4px 0">Tu decides</td></tr>
                    <tr><td style="font-size:12px;color:#6b7b5e;line-height:1.4">Aceptas o rechazas cada trabajo</td></tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:25px 40px 35px 40px;text-align:center">
            <p style="font-size:14px;color:#4a5a3a;margin:0 0 16px 0">Mientras tanto, puedes ir familiarizandote con tu panel:</p>
            <a href="https://www.certificadoya.es/panel-tecnicos.html" style="display:inline-block;padding:12px 30px;background:#547c24;color:#ffffff;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none">Acceder al panel de tecnico</a>
          </td>
        </tr>
        <tr>
          <td style="background:#1a1a1a;padding:25px 40px;text-align:center">
            <a href="https://www.certificadoya.es" style="font-size:18px;font-weight:700;color:#ffffff;text-decoration:none">CertificadoYa</a>
            <div style="margin-top:12px">
              <a href="https://www.certificadoya.es" style="color:#b8d4a0;font-size:12px;text-decoration:none;padding:0 8px">Web</a>
              <a href="https://www.certificadoya.es/blog/" style="color:#b8d4a0;font-size:12px;text-decoration:none;padding:0 8px">Blog</a>
              <a href="https://www.certificadoya.es/panel-tecnicos.html" style="color:#b8d4a0;font-size:12px;text-decoration:none;padding:0 8px">Tecnicos</a>
            </div>
            <p style="font-size:11px;color:#6b7b5e;margin:12px 0 0 0;line-height:1.5">&copy; 2026 CertificadoYa &mdash; ArtStudio</p>
          </td>
        </tr>
      </table>
      <p style="font-size:11px;color:#9aab8a;margin-top:20px;text-align:center">Este email se ha enviado automaticamente al registrarte en CertificadoYa.</p>
    </td></tr>
  </table>
</body>
</html>`;

      // Email a Arturo (version texto)
      const emailArturo = `Nuevo registro de tecnico en CertificadoYa

Nombre: ${t.nombre}
Email: ${t.email}
Telefono: ${t.telefono || 'No indicado'}
Profesion: ${t.profesion}
Colegiado: ${t.colegiado}
Provincias: ${t.provincias}
Web: ${t.web || 'No indicada'}
Perfil: ${perfilUrl}`;

      // Enviar emails con la API de email de Cloudflare Workers
      if (typeof env.EMAIL !== 'undefined') {
        await env.EMAIL.send({
          to: 'aparejado@me.com',
          subject: `Nuevo tecnico: ${t.nombre} - ${t.profesion}`,
          text: emailArturo,
        });

        await env.EMAIL.send({
          to: t.email,
          subject: `Bienvenido a CertificadoYa, ${t.nombre} - Tu perfil de tecnico`,
          html: emailHtml,
        });
      } else {
        console.log('EMAIL binding not configured. Would send:');
        console.log('To Arturo:', emailArturo);
        console.log('To tecnico:', emailHtml.substring(0, 200) + '...');
      }

      return new Response(JSON.stringify({ok: true, id, perfil_url: perfilUrl}), {
        headers: {'Content-Type': 'application/json'}
      });

    } catch (err) {
      return new Response(JSON.stringify({ok: false, error: err.message}), {status: 500});
    }
  }
};
