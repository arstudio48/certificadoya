/**
 * CertificadoYa Chatbot Widget v1.0
 * Chatbot flotante con FAQ precargado + captura de leads.
 * Sin dependencias externas. Sin LLM. No se cae nunca.
 */
(function () {
  'use strict';

  // ── Config ──────────────────────────────────────────────
  const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co';
  const SUPABASE_ANON = 'sb_publishable_MsDx5jVGtDAzoB3l3-8DiQ_BxWpChA0';
  const WHATSAPP_NUMBER = '34608563002'; // sin + ni espacios

  // ── FAQ Data ─────────────────────────────────────────────
  const FAQ = [
    {
      q: '¿Qué es el certificado de eficiencia energética (CEE)?',
      a: 'El **Certificado de Eficiencia Energética (CEE)** es un documento oficial que mide el consumo de energía de una vivienda o local, asignándole una etiqueta de la A (más eficiente) a la G (menos eficiente). Es obligatorio para vender o alquilar cualquier inmueble en España.'
    },
    {
      q: '¿Cuánto cuesta el certificado energético?',
      a: 'En CertificadoYa los precios van desde **45€** para pisos pequeños en provincia, hasta **60-75€** para viviendas grandes en Madrid o Barcelona capital. El presupuesto es instantáneo — solo necesitas los metros cuadrados y la ubicación.'
    },
    {
      q: '¿Cuánto tarda?',
      a: 'Normalmente **48-96 horas** desde que el técnico visita el inmueble. En Madrid y Barcelona a veces en **24h** si hay disponibilidad.'
    },
    {
      q: '¿Es obligatorio el CEE para alquilar?',
      a: '**Sí.** Desde 2013 es obligatorio tener el CEE para cualquier contrato de alquiler. Sin CEE no puedes alquilar legalmente y te expones a sanciones de hasta **6.000€**.'
    },
    {
      q: '¿Es obligatorio para vender?',
      a: '**Sí.** Es obligatorio mostrar la etiqueta energética en cualquier anuncio de venta. Desde 2025 (RD 659/2025) las sanciones son más severas. Sin CEE no puedes firmar la escritura.'
    },
    {
      q: '¿Qué necesito para pedir el certificado?',
      a: 'Muy poco: la dirección del inmueble, los metros cuadrados aproximados, y tu nombre y teléfono. El técnico se encarga del resto durante la visita.'
    },
    {
      q: '¿Cuánto dura el certificado?',
      a: 'El CEE tiene una validez de **10 años** para viviendas (5 años para edificios terciarios grandes). Si haces reformas importantes que afecten al consumo, deberías renovarlo antes.'
    },
    {
      q: '¿Hay ayudas o subvenciones?',
      a: '**Sí.** El Plan Next Generation de la UE financia rehabilitaciones energéticas. Las ayudas pueden cubrir hasta el **40-80%** del coste de mejoras (aislamiento, ventanas, calderas). En CertificadoYa te informamos sin compromiso.'
    },
    {
      q: '¿Hacéis certificados para garajes o trasteros?',
      a: 'Los **garajes y trasteros** no necesitan CEE en la mayoría de los casos. Si tu garaje tiene consumo propio (ventilación, iluminación), puede necesitarlo. Consúltanos sin compromiso.'
    },
    {
      q: '¿Puedo hacer el certificado online sin visita?',
      a: 'En algunos casos sí — para inmuebles muy pequeños o si tienes planos del arquitecto con todos los datos constructivos. Pero lo normal es que un técnico certificador **visite el inmueble** para medir y tomar datos.'
    },
    {
      q: '¿Qué multas hay por no tener CEE?',
      a: 'Las sanciones van desde **300€ hasta 6.000€** dependiendo de la gravedad. Desde el RD 659/2025, las inspecciones son más frecuentes, sobre todo en alquileres turísticos y viviendas anunciadas en portales inmobiliarios.'
    },
    {
      q: '¿Cómo sé si un técnico es de confianza?',
      a: 'En CertificadoYa **verificamos** a todos los técnicos antes de darles de alta. Solo trabajamos con arquitectos, ingenieros y aparejadores colegiados. Todos tienen seguro de responsabilidad civil.'
    }
  ];

  const RESPUESTA_RAPIDA = 'No tengo esa información, pero puedo ayudarte a solicitar tu presupuesto gratuito en menos de 1 minuto.';

  // ── Estilos CSS inyectados ──────────────────────────────
  const CSS = `
#cy-chatbot-btn {
  position: fixed; bottom: 24px; right: 24px; z-index: 999999;
  width: 60px; height: 60px; border-radius: 50%;
  background: linear-gradient(135deg, #1a5c2e, #2e8b47);
  color: #fff; border: none; cursor: pointer;
  box-shadow: 0 4px 20px rgba(26,92,46,.35);
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; transition: transform .2s, box-shadow .2s;
}
#cy-chatbot-btn:hover { transform: scale(1.08); box-shadow: 0 6px 28px rgba(26,92,46,.45); }

#cy-chatbot-panel {
  position: fixed; bottom: 96px; right: 24px; z-index: 999998;
  width: 360px; max-height: 560px;
  background: #fff; border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0,0,0,.15);
  display: none; flex-direction: column;
  font-family: 'DM Sans', 'Outfit', Arial, sans-serif;
  overflow: hidden; border: 1px solid #e5e7eb;
}

#cy-chatbot-panel.open { display: flex; }

#cy-chatbot-header {
  background: linear-gradient(135deg, #1a5c2e, #2e8b47);
  color: #fff; padding: 16px 20px;
  display: flex; align-items: center; justify-content: space-between;
  font-weight: 600; font-size: 15px;
}
#cy-chatbot-close { background: none; border: none; color: #b8d4a0; font-size: 20px; cursor: pointer; padding: 0; line-height: 1; }

#cy-chatbot-messages {
  flex: 1; overflow-y: auto; padding: 16px;
  display: flex; flex-direction: column; gap: 8px;
  min-height: 280px; max-height: 360px;
}
.cy-msg-bot, .cy-msg-user {
  max-width: 85%; padding: 10px 14px; border-radius: 12px;
  font-size: 13.5px; line-height: 1.45;
}
.cy-msg-bot { background: #f3f9eb; color: #20201f; align-self: flex-start; border-bottom-left-radius: 4px; }
.cy-msg-bot strong { color: #1a5c2e; }
.cy-msg-user { background: #e8f0fe; color: #20201f; align-self: flex-end; border-bottom-right-radius: 4px; }
.cy-faq-btn {
  display: block; width: 100%; text-align: left;
  background: #fff; border: 1px solid #dce8d0;
  border-radius: 8px; padding: 10px 12px;
  font-size: 13px; color: #20201f; cursor: pointer;
  transition: background .15s, border-color .15s;
  margin: 2px 0; font-family: inherit;
}
.cy-faq-btn:hover { background: #f0fdf4; border-color: #2e8b47; }

#cy-chatbot-input-area {
  padding: 12px 16px; border-top: 1px solid #e5e7eb;
  display: flex; gap: 8px;
}
#cy-chatbot-input {
  flex: 1; border: 1px solid #d1d5db; border-radius: 8px;
  padding: 8px 12px; font-size: 13px; font-family: inherit; outline: none;
}
#cy-chatbot-input:focus { border-color: #2e8b47; }
#cy-chatbot-send {
  background: #2e8b47; color: #fff; border: none;
  border-radius: 8px; padding: 8px 16px; font-size: 13px;
  font-weight: 600; cursor: pointer; transition: background .15s;
}
#cy-chatbot-send:hover { background: #1a5c2e; }

.cy-chatbot-cta {
  background: linear-gradient(135deg, #1a5c2e, #2e8b47);
  color: #fff; border: none; border-radius: 8px;
  padding: 10px 16px; font-size: 13px; font-weight: 600;
  cursor: pointer; display: block; width: 100%;
  margin: 4px 0; text-align: center; text-decoration: none;
  font-family: inherit;
}
.cy-chatbot-cta:hover { opacity: .92; }
.cy-chatbot-whatsapp {
  background: #25D366; color: #fff;
}
.cy-chatbot-whatsapp:hover { background: #1da851; }

#cy-chatbot-form { padding: 0 16px 12px; display: flex; flex-direction: column; gap: 8px; }
#cy-chatbot-form input {
  border: 1px solid #d1d5db; border-radius: 8px;
  padding: 10px 12px; font-size: 13px; font-family: inherit; outline: none;
}
#cy-chatbot-form input:focus { border-color: #2e8b47; }
#cy-chatbot-form .cy-error { color: #dc2626; font-size: 12px; margin: 0; }

@media(max-width:480px){
  #cy-chatbot-panel { width: calc(100vw - 32px); right: 16px; bottom: 88px; max-height: 480px; }
  #cy-chatbot-btn { width: 52px; height: 52px; font-size: 22px; bottom: 18px; right: 18px; }
}
`;

  // ── Estado ──────────────────────────────────────────────
  let step = 'greeting'; // greeting | chat | form | form_submit
  let nombre = '';
  let telefono = '';
  let email = '';

  // ── Inyectar CSS ──────────────────────────────────────
  const styleEl = document.createElement('style');
  styleEl.textContent = CSS;
  document.head.appendChild(styleEl);

  // ── Construir HTML ──────────────────────────────────────
  const panel = document.createElement('div');
  panel.id = 'cy-chatbot-panel';
  panel.innerHTML = `
    <div id="cy-chatbot-header">
      <span>💬 CertificadoYa</span>
      <button id="cy-chatbot-close">&times;</button>
    </div>
    <div id="cy-chatbot-messages"></div>
    <div id="cy-chatbot-input-area">
      <input id="cy-chatbot-input" type="text" placeholder="Escribe tu pregunta..." autocomplete="off">
      <button id="cy-chatbot-send">Enviar</button>
    </div>
    <form id="cy-chatbot-form" style="display:none">
      <input id="cy-form-nombre" type="text" placeholder="Tu nombre *" required>
      <input id="cy-form-telefono" type="tel" placeholder="Teléfono *" required>
      <input id="cy-form-email" type="email" placeholder="Email (opcional)">
      <input id="cy-form-provincia" type="text" placeholder="Provincia *" required>
      <input id="cy-form-metros" type="number" placeholder="Metros cuadrados aprox.">
      <p class="cy-error" id="cy-form-error" style="display:none"></p>
      <button type="submit" class="cy-chatbot-cta" id="cy-form-submit">Solicitar presupuesto</button>
      <p style="font-size:11px;color:#999;text-align:center;margin:2px 0">
        Te llamamos en menos de 24h
      </p>
    </form>
  `;

  const btn = document.createElement('button');
  btn.id = 'cy-chatbot-btn';
  btn.innerHTML = '💬';
  btn.setAttribute('aria-label', 'Abrir chat CertificadoYa');

  document.body.appendChild(btn);
  document.body.appendChild(panel);

  // ── Referencias ──────────────────────────────────────────
  const msgContainer = document.getElementById('cy-chatbot-messages');
  const input = document.getElementById('cy-chatbot-input');
  const sendBtn = document.getElementById('cy-chatbot-send');
  const closeBtn = document.getElementById('cy-chatbot-close');
  const form = document.getElementById('cy-chatbot-form');
  const formNombre = document.getElementById('cy-form-nombre');
  const formTelefono = document.getElementById('cy-form-telefono');
  const formEmail = document.getElementById('cy-form-email');
  const formProvincia = document.getElementById('cy-form-provincia');
  const formMetros = document.getElementById('cy-form-metros');
  const formError = document.getElementById('cy-form-error');
  const formSubmit = document.getElementById('cy-form-submit');

  // ── Funciones ──────────────────────────────────────────
  function addBotMessage(html, withCTA = false) {
    const div = document.createElement('div');
    div.className = 'cy-msg-bot';
    div.innerHTML = html.replace(/\n/g, '<br>');
    msgContainer.appendChild(div);
    msgContainer.scrollTop = msgContainer.scrollHeight;

    if (withCTA) {
      const cta = document.createElement('button');
      cta.className = 'cy-chatbot-cta';
      cta.textContent = '💰 Pedir presupuesto ahora';
      cta.onclick = showForm;
      msgContainer.appendChild(cta);
      msgContainer.scrollTop = msgContainer.scrollHeight;
    }
  }

  function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'cy-msg-user';
    div.textContent = text;
    msgContainer.appendChild(div);
    msgContainer.scrollTop = msgContainer.scrollHeight;
  }

  function showFAQ() {
    addBotMessage('**Hola! 👋** Soy el asistente de CertificadoYa. ¿Qué quieres saber?');
    FAQ.forEach((item, i) => {
      const btn2 = document.createElement('button');
      btn2.className = 'cy-faq-btn';
      btn2.textContent = item.q;
      btn2.onclick = function () {
        addBotMessage('**' + item.q + '**<br>' + item.a, true);
        // Ofrecer más opciones
        setTimeout(() => {
          const btn3 = document.createElement('button');
          btn3.className = 'cy-faq-btn';
          btn3.textContent = '❓ Otra pregunta';
          btn3.onclick = () => { msgContainer.innerHTML = ''; showFAQ(); };
          msgContainer.appendChild(btn3);
          const btn4 = document.createElement('button');
          btn4.className = 'cy-chatbot-cta';
          btn4.textContent = '💰 Solicitar presupuesto';
          btn4.onclick = showForm;
          msgContainer.appendChild(btn4);
          msgContainer.scrollTop = msgContainer.scrollHeight;
        }, 300);
      };
      msgContainer.appendChild(btn2);
    });
    msgContainer.scrollTop = msgContainer.scrollHeight;
  }

  function showForm() {
    addBotMessage('Rellena estos datos y te llamamos en **menos de 24 horas** con un presupuesto personalizado 📋');
    form.style.display = 'flex';
    input.disabled = true;
    sendBtn.disabled = true;
    input.style.display = 'none';
    sendBtn.style.display = 'none';
    step = 'form';
  }

  function handleTextInput(text) {
    if (!text.trim()) return;
    addUserMessage(text);

    const lower = text.toLowerCase();
    let found = false;

    // Buscar en FAQ
    for (const item of FAQ) {
      if (item.q.toLowerCase().includes(lower)) {
        addBotMessage('**' + item.q + '**<br>' + item.a, true);
        found = true;
        break;
      }
    }

    if (!found) {
      // Buscar por palabras clave
      if (lower.includes('precio') || lower.includes('cost') || lower.includes('tarifa') || lower.includes('€') || lower.includes('euro') || lower.includes('cuanto') || lower.includes('cuesta')) {
        addBotMessage('Nuestros precios van desde **45€** para pisos pequeños en provincia. El presupuesto es **instantáneo** y sin compromiso. Puedes calcularlo ahora mismo.', true);
      } else if (lower.includes('obligatorio') || lower.includes('necesito') || lower.includes('multa') || lower.includes('sancion') || lower.includes('ley')) {
        addBotMessage('**Sí**, el CEE es obligatorio para vender o alquilar desde 2013. Las multas van de 300€ a 6.000€. Si tienes un inmueble en venta o alquiler, necesitas el certificado **sí o sí**.', true);
      } else if (lower.includes('tiempo') || lower.includes('tarda') || lower.includes('día') || lower.includes('horas') || lower.includes('urgente')) {
        addBotMessage('Normalmente **48-96 horas** desde la visita del técnico. En Madrid y Barcelona a veces en **24h**.', true);
      } else if (lower.includes('subvencion') || lower.includes('ayuda') || lower.includes('next') || lower.includes('fondos') || lower.includes('rehabilitacion')) {
        addBotMessage('**Sí hay ayudas.** El plan Next Generation cubre hasta el **80%** de rehabilitaciones energéticas (aislamiento, ventanas, calderas eficientes). Te informamos sin compromiso.', true);
      } else if (lower.includes('gracias') || lower.includes('vale') || lower.includes('ok') || lower.includes('entendido')) {
        addBotMessage('¡De nada! Si necesitas presupuesto, solo pídemelo 💚');
      } else if (lower.includes('adios') || lower.includes('hastaluego') || lower.includes('chao') || lower.includes('bye')) {
        addBotMessage('¡Hasta luego! Si te surge algo más, aquí estoy 👋');
      } else {
        // Respuesta genérica + FAQ
        addBotMessage(RESPUESTA_RAPIDA);
        setTimeout(() => {
          addBotMessage('Aquí tienes las preguntas más frecuentes:');
          FAQ.forEach((item, i) => {
            const btn5 = document.createElement('button');
            btn5.className = 'cy-faq-btn';
            btn5.textContent = item.q;
            btn5.onclick = function () {
              msgContainer.innerHTML = '';
              addBotMessage('**' + item.q + '**<br>' + item.a, true);
              const btn6 = document.createElement('button');
              btn6.className = 'cy-faq-btn';
              btn6.textContent = '❓ Más preguntas';
              btn6.onclick = () => { msgContainer.innerHTML = ''; showFAQ(); };
              msgContainer.appendChild(btn6);
              const btn7 = document.createElement('button');
              btn7.className = 'cy-chatbot-cta';
              btn7.textContent = '💰 Solicitar presupuesto';
              btn7.onclick = showForm;
              msgContainer.appendChild(btn7);
            };
            msgContainer.appendChild(btn5);
          });
          msgContainer.scrollTop = msgContainer.scrollHeight;
        }, 400);
      }
    }
    input.value = '';
  }

  function submitForm(e) {
    e.preventDefault();
    const nombre2 = formNombre.value.trim();
    const tel = formTelefono.value.trim();
    const em = formEmail.value.trim();
    const prov = formProvincia.value.trim();
    const metros = formMetros.value.trim();

    formError.style.display = 'none';

    if (!nombre2 || !tel || !prov) {
      formError.textContent = 'Rellena nombre, teléfono y provincia.';
      formError.style.display = 'block';
      return;
    }
    if (tel.length < 9) {
      formError.textContent = 'El teléfono no es válido (mín. 9 dígitos).';
      formError.style.display = 'block';
      return;
    }

    formSubmit.disabled = true;
    formSubmit.textContent = 'Enviando...';
    addBotMessage('¡Gracias! Estamos procesando tu solicitud...');

    // Enviar a Supabase
    const payload = {
      nombre_cliente: nombre2,
      telefono: tel,
      email: em || null,
      provincia: prov,
      metros_cuadrados: metros ? parseInt(metros) : null,
      tipo_inmueble: 'vivienda',
      estado: 'nuevo',
      origen: 'chatbot',
      created_at: new Date().toISOString()
    };

    fetch(SUPABASE_URL + '/rest/v1/leads', {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_ANON,
        'Authorization': 'Bearer ' + SUPABASE_ANON,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify(payload)
    })
      .then(r => {
        if (r.ok || r.status === 201) {
          form.innerHTML = `
            <div style="text-align:center;padding:16px">
              <div style="font-size:36px;margin-bottom:8px">✅</div>
              <p style="font-weight:600;color:#1a5c2e;margin:0 0 4px">¡Recibido!</p>
              <p style="font-size:13px;color:#666;margin:0">Te llamamos en menos de 24h.</p>
              <a href="https://wa.me/${WHATSAPP_NUMBER}" target="_blank" class="cy-chatbot-cta cy-chatbot-whatsapp" style="margin-top:12px;text-decoration:none">
                📱 Hablar por WhatsApp
              </a>
            </div>`;
          addBotMessage('**¡Solicitud recibida!** 🎉 Te contactamos pronto.');
        } else {
          throw new Error('HTTP ' + r.status);
        }
      })
      .catch(err => {
        formSubmit.disabled = false;
        formSubmit.textContent = 'Solicitar presupuesto';
        formError.textContent = 'Error al enviar. Intenta de nuevo o llama al 608563002.';
        formError.style.display = 'block';
      });
  }

  // ── Eventos ──────────────────────────────────────────
  btn.onclick = function () {
    const isOpen = panel.classList.toggle('open');
    if (isOpen && msgContainer.children.length === 0) {
      showFAQ();
    }
    btn.style.display = isOpen ? 'none' : 'flex';
  };

  closeBtn.onclick = function () {
    panel.classList.remove('open');
    btn.style.display = 'flex';
  };

  sendBtn.onclick = function () {
    handleTextInput(input.value);
  };

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleTextInput(input.value);
    }
  });

  form.onsubmit = submitForm;

  // Cerrar con Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && panel.classList.contains('open')) {
      panel.classList.remove('open');
      btn.style.display = 'flex';
    }
  });
})();
