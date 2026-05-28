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

      // Email a Arturo (aviso de nuevo registro)
      const emailContent = `
Nuevo registro de tecnico en CertificadoYa

Nombre: ${t.nombre}
Email: ${t.email}
Telefono: ${t.telefono || 'No indicado'}
Profesion: ${t.profesion}
Colegiado: ${t.colegiado}
Provincias: ${t.provincias}
Web: ${t.web || 'No indicada'}

Para gestionar: https://www.certificadoya.es/admin/tecnicos.html?id=${id}
`;

      await env.EMAIL.send({
        to: 'aparejado@me.com',
        subject: `Nuevo tecnico: ${t.nombre} - ${t.profesion}`,
        text: emailContent,
      });

      // Email automatico al tecnico con instrucciones
      const slug = t.nombre.toLowerCase()
        .replace(/[áàäâ]/g, 'a').replace(/[éèëê]/g, 'e').replace(/[íìïî]/g, 'i')
        .replace(/[óòöô]/g, 'o').replace(/[úùüû]/g, 'u').replace(/ñ/g, 'n')
        .replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');

      const perfilUrl = `https://www.certificadoya.es/tecnicos/${slug}/`;
      const snippetHtml = `<a href="${perfilUrl}" rel="nofollow" target="_blank">Colaboro con CertificadoYa</a>`;

      const emailTecnico = `
Hola ${t.nombre},

Gracias por registrarte en CertificadoYa. Hemos recibido tu solicitud y la estamos revisando.

? TU PERFIL PUBLICO
Cuando verifiquemos tus datos, tu perfil estara disponible en:
${perfilUrl}

? COMPARTE TU PERFIL
Pon este enlace en tu web o en tu firma de email para que tus clientes te encuentren:

${perfilUrl}

? PARA QUE TE ENLACEMOS DESDE TU WEB (opcional, recomendado)
Si tienes una pagina web, copia y pega este codigo donde quieras mostrar tu colaboracion con nosotros:

${snippetHtml}

Eso es todo lo que necesitas. Si tienes cualquier duda, respondemos a este mismo email.

Un saludo,
Equipo de CertificadoYa
certificadoya.es`;

      await env.EMAIL.send({
        to: t.email,
        subject: `Bienvenido a CertificadoYa - Tu perfil de tecnico`,
        text: emailTecnico,
      });

      return new Response(JSON.stringify({ok: true, id}), {
        headers: {'Content-Type': 'application/json'}
      });

    } catch (err) {
      return new Response(JSON.stringify({ok: false, error: err.message}), {status: 500});
    }
  }
};
