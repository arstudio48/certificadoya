/* Blog Preguntas Widget — Sección de preguntas en artículos del blog solo para usuarios registrados */
(function() {
  'use strict';

  var API = 'https://wypgqpgjlookbhuaiyxa.supabase.co/functions/v1/blog-preguntas';
  var SLUG = document.querySelector('[data-slug]') ? document.querySelector('[data-slug]').getAttribute('data-slug') : '';
  var STORAGE_KEY = 'certificadoya_blog_user';

  if (!SLUG) {
    // Try to extract slug from canonical URL or path
    var canon = document.querySelector('link[rel="canonical"]');
    if (canon) {
      var parts = canon.href.split('/');
      SLUG = parts[parts.length - 1].replace('.html', '') || parts[parts.length - 2];
    }
    if (!SLUG) SLUG = window.location.pathname.split('/').pop().replace('.html', '') || 'unknown';
  }

  var currentUser = null;

  // Load user from localStorage
  try {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored) currentUser = JSON.parse(stored);
  } catch(e) {}

  // ── Styles ──
  var style = document.createElement('style');
  style.textContent = `
    .bpreg-wrap { max-width: 720px; margin: 2.5rem auto 1rem; padding: 0 1.5rem; }
    .bpreg-header { display: flex; align-items: center; gap: .75rem; margin-bottom: 1.5rem; }
    .bpreg-header h3 { font-size: 1.1rem; font-weight: 700; color: #2d3a1f; margin: 0; }
    .bpreg-header .bpreg-count { font-size: .8rem; color: #9aab8a; background: #f3f9eb; padding: .15rem .55rem; border-radius: 20px; font-weight: 500; }

    .bpreg-login { background: white; border: 1px solid #e8ece6; border-radius: 12px; padding: 1.5rem; text-align: center; }
    .bpreg-login h4 { font-size: .95rem; color: #2d3a1f; margin: 0 0 .35rem; }
    .bpreg-login p { font-size: .82rem; color: #6b7b5e; margin: 0 0 1rem; line-height: 1.5; }
    .bpreg-login input { width: 100%; max-width: 320px; padding: .65rem .85rem; border: 1.5px solid #dce4d5; border-radius: 10px; font-size: .9rem; font-family: inherit; text-align: center; box-sizing: border-box; }
    .bpreg-login input:focus { outline: none; border-color: #547c24; box-shadow: 0 0 0 3px rgba(84,124,36,.1); }
    .bpreg-login .btn { display: inline-block; padding: .65rem 1.5rem; background: #547c24; color: white; border: none; border-radius: 10px; font-size: .9rem; font-weight: 600; cursor: pointer; font-family: inherit; margin-top: .5rem; transition: background .15s; }
    .bpreg-login .btn:hover { background: #45691d; }
    .bpreg-login .btn:disabled { background: #a0b88a; cursor: not-allowed; }
    .bpreg-login .bpreg-msg { font-size: .82rem; margin-top: .5rem; }
    .bpreg-login .bpreg-msg.ok { color: #547c24; }
    .bpreg-login .bpreg-msg.err { color: #c0392b; }

    .bpreg-codigo-inputs { display: flex; gap: .4rem; justify-content: center; margin: .75rem 0; }
    .bpreg-codigo-inputs input { width: 42px; height: 48px; text-align: center; font-size: 1.3rem; font-weight: 700; border: 1.5px solid #dce4d5; border-radius: 10px; padding: 0; }

    .bpreg-form { display: none; }
    .bpreg-form textarea { width: 100%; padding: .75rem; border: 1.5px solid #dce4d5; border-radius: 10px; font-size: .9rem; font-family: inherit; resize: vertical; min-height: 80px; box-sizing: border-box; }
    .bpreg-form textarea:focus { outline: none; border-color: #547c24; box-shadow: 0 0 0 3px rgba(84,124,36,.1); }
    .bpreg-form .bpreg-form-row { display: flex; align-items: center; gap: .75rem; margin-top: .5rem; }
    .bpreg-form .bpreg-form-row .btn { padding: .6rem 1.25rem; background: #547c24; color: white; border: none; border-radius: 10px; font-size: .85rem; font-weight: 600; cursor: pointer; font-family: inherit; transition: background .15s; }
    .bpreg-form .bpreg-form-row .btn:hover { background: #45691d; }
    .bpreg-form .bpreg-form-row .btn:disabled { background: #a0b88a; cursor: not-allowed; }
    .bpreg-form .bpreg-form-row .bpreg-user { font-size: .8rem; color: #6b7b5e; }
    .bpreg-form .bpreg-form-row .bpreg-logout { font-size: .78rem; color: #c0392b; cursor: pointer; background: none; border: none; text-decoration: underline; font-family: inherit; }

    .bpreg-list { margin-top: 1.25rem; }
    .bpreg-item { padding: 1rem; border: 1px solid #e8ece6; border-radius: 10px; margin-bottom: .6rem; background: white; }
    .bpreg-item .bpreg-item-q { font-size: .88rem; color: #2d3a1f; line-height: 1.5; margin: 0 0 .35rem; }
    .bpreg-item .bpreg-item-meta { font-size: .75rem; color: #9aab8a; }
    .bpreg-item .bpreg-item-a { margin-top: .5rem; padding: .6rem .75rem; background: #f3f9eb; border-radius: 8px; font-size: .85rem; color: #3d5a1e; line-height: 1.5; }
    .bpreg-item .bpreg-item-a::before { content: 'Respuesta: '; font-weight: 600; }

    .bpreg-empty { text-align: center; padding: 2rem 0; color: #9aab8a; font-size: .85rem; }
    .bpreg-loading { text-align: center; padding: 1rem 0; color: #9aab8a; font-size: .82rem; }
  `;
  document.head.appendChild(style);

  // ── Build widget container ──
  var wrap = document.createElement('div');
  wrap.className = 'bpreg-wrap';
  wrap.id = 'bpreg-wrap';
  wrap.innerHTML = '<div class="bpreg-loading">Cargando...</div>';

  // ── Insert before footer or at end of article ──
  function insertWidget() {
    var main = document.querySelector('main') || document.querySelector('article') || document.querySelector('.post-content') || document.querySelector('.blog-content');
    var footer = document.querySelector('footer');
    if (main && main.nextSibling) {
      main.parentNode.insertBefore(wrap, main.nextSibling);
    } else if (footer && footer.parentNode) {
      footer.parentNode.insertBefore(wrap, footer);
    } else {
      document.body.appendChild(wrap);
    }
  }

  // ── Functions ──
  function saveUser(user) {
    currentUser = user;
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(user)); } catch(e) {}
  }

  function logout() {
    currentUser = null;
    try { localStorage.removeItem(STORAGE_KEY); } catch(e) {}
    renderWidget();
  }

  function encodeEmail(email) {
    return email.replace(/\./g, '_').replace(/@/g, '_at_');
  }

  async function loadQuestions() {
    try {
      var res = await fetch(API + '?action=preguntas&slug=' + encodeURIComponent(SLUG));
      var data = await res.json();
      return data.preguntas || [];
    } catch(e) {
      return [];
    }
  }

  async function submitQuestion(pregunta) {
    var res = await fetch(API + '?action=preguntar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: currentUser.email,
        user_name: currentUser.nombre || '',
        pregunta: pregunta,
        articulo_slug: SLUG,
      }),
    });
    return res.ok;
  }

  async function sendLoginCode(email) {
    var res = await fetch(API + '?action=enviar-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email }),
    });
    var data = await res.json();
    return data;
  }

  async function verifyCode(email, codigo) {
    var res = await fetch(API + '?action=verificar-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, codigo: codigo }),
    });
    var data = await res.json();
    if (data.success) saveUser(data.user);
    return data;
  }

  // ── Render ──
  function renderWidget() {
    if (currentUser) {
      renderLoggedIn();
    } else {
      renderLogin();
    }
  }

  function renderLogin() {
    var emailSent = false;
    var emailAddr = '';
    wrap.innerHTML = `
      <div class="bpreg-header">
        <h3>💬 Preguntas sobre este artículo</h3>
      </div>
      <div class="bpreg-login" id="bpreg-login-view">
        <h4>Inicia sesión para preguntar</h4>
        <p>Deja tu pregunta y los técnicos de CertificadoYa te responderán.</p>
        <div id="bpreg-login-step1">
          <input type="email" id="bpreg-email" placeholder="Tu email" autocomplete="email">
          <div class="bpreg-msg" id="bpreg-msg1"></div>
          <button class="btn" id="bpreg-btn-send">Enviar código</button>
        </div>
        <div id="bpreg-login-step2" style="display:none">
          <p style="margin-bottom:.5rem">Te hemos enviado un código a <strong id="bpreg-email-display"></strong></p>
          <div class="bpreg-codigo-inputs">
            <input type="text" maxlength="1" class="bpreg-digit" data-idx="0">
            <input type="text" maxlength="1" class="bpreg-digit" data-idx="1">
            <input type="text" maxlength="1" class="bpreg-digit" data-idx="2">
            <input type="text" maxlength="1" class="bpreg-digit" data-idx="3">
            <input type="text" maxlength="1" class="bpreg-digit" data-idx="4">
            <input type="text" maxlength="1" class="bpreg-digit" data-idx="5">
          </div>
          <div class="bpreg-msg" id="bpreg-msg2"></div>
          <button class="btn" id="bpreg-btn-verify" style="display:none">Verificar</button>
          <br>
          <a href="#" id="bpreg-resend" style="font-size:.78rem;color:#9aab8a;margin-top:.5rem;display:inline-block">Reenviar código</a>
        </div>
      </div>
      <div class="bpreg-list" id="bpreg-list"></div>
    `;

    // Load existing questions
    loadQuestions().then(function(qs) {
      renderQuestions(qs);
    });

    // Step 1: Send code
    document.getElementById('bpreg-btn-send').onclick = async function() {
      var email = document.getElementById('bpreg-email').value.trim();
      if (!email || !email.includes('@')) {
        showMsg('bpreg-msg1', 'Introduce un email válido', 'err');
        return;
      }
      emailAddr = email;
      this.disabled = true;
      this.textContent = 'Enviando...';
      var result = await sendLoginCode(email);
      if (result.success) {
        emailSent = true;
        document.getElementById('bpreg-login-step1').style.display = 'none';
        document.getElementById('bpreg-login-step2').style.display = 'block';
        document.getElementById('bpreg-email-display').textContent = email;
        document.querySelector('.bpreg-digit').focus();
      } else {
        showMsg('bpreg-msg1', 'Error al enviar el código. Intenta de nuevo.', 'err');
        this.disabled = false;
        this.textContent = 'Enviar código';
      }
    };

    // Step 2: Digit inputs auto-advance
    var digits = document.querySelectorAll('.bpreg-digit');
    digits.forEach(function(inp, i) {
      inp.addEventListener('input', function() {
        if (this.value && i < 5) digits[i+1].focus();
        // Auto-verify when all 6 digits filled
        var code = '';
        digits.forEach(function(d) { code += d.value; });
        if (code.length === 6) {
          document.getElementById('bpreg-btn-verify').click();
        }
      });
      inp.addEventListener('keydown', function(e) {
        if (e.key === 'Backspace' && !this.value && i > 0) {
          digits[i-1].focus();
          digits[i-1].value = '';
        }
      });
    });

    // Verify button
    document.getElementById('bpreg-btn-verify').onclick = async function() {
      var code = '';
      digits.forEach(function(d) { code += d.value; });
      if (code.length !== 6) {
        showMsg('bpreg-msg2', 'Introduce el código completo de 6 dígitos', 'err');
        return;
      }
      this.disabled = true;
      this.textContent = 'Verificando...';
      var result = await verifyCode(emailAddr, code);
      if (result.success) {
        renderWidget();
      } else {
        showMsg('bpreg-msg2', result.error || 'Código incorrecto', 'err');
        this.disabled = false;
        this.textContent = 'Verificar';
        // Clear digits on error
        digits.forEach(function(d) { d.value = ''; });
        digits[0].focus();
      }
    };

    // Resend
    document.getElementById('bpreg-resend').onclick = function(e) {
      e.preventDefault();
      sendLoginCode(emailAddr);
      showMsg('bpreg-msg2', 'Código reenviado. Revisa tu email.', 'ok');
    };
  }

  function renderLoggedIn() {
    wrap.innerHTML = `
      <div class="bpreg-header">
        <h3>💬 Preguntas sobre este artículo</h3>
        <span class="bpreg-count" id="bpreg-count">0</span>
      </div>
      <div class="bpreg-form" id="bpreg-form" style="display:block">
        <textarea id="bpreg-pregunta" placeholder="Escribe tu pregunta aquí..." maxlength="500"></textarea>
        <div class="bpreg-form-row">
          <button class="btn" id="bpreg-btn-ask">Preguntar</button>
          <span class="bpreg-user">${currentUser.email}</span>
          <button class="bpreg-logout" id="bpreg-logout">Cerrar sesión</button>
        </div>
        <div class="bpreg-msg" id="bpreg-msg-ask"></div>
      </div>
      <div class="bpreg-list" id="bpreg-list"></div>
    `;

    document.getElementById('bpreg-logout').onclick = function(e) {
      e.preventDefault();
      logout();
    };

    document.getElementById('bpreg-btn-ask').onclick = async function() {
      var pregunta = document.getElementById('bpreg-pregunta').value.trim();
      if (!pregunta || pregunta.length < 10) {
        showMsg('bpreg-msg-ask', 'La pregunta debe tener al menos 10 caracteres', 'err');
        return;
      }
      this.disabled = true;
      this.textContent = 'Enviando...';
      var ok = await submitQuestion(pregunta);
      if (ok) {
        document.getElementById('bpreg-pregunta').value = '';
        showMsg('bpreg-msg-ask', '✅ Pregunta enviada. Los técnicos la responderán pronto.', 'ok');
        // Reload questions
        var qs = await loadQuestions();
        renderQuestions(qs);
      } else {
        showMsg('bpreg-msg-ask', 'Error al enviar. Intenta de nuevo.', 'err');
      }
      this.disabled = false;
      this.textContent = 'Preguntar';
    };

    loadQuestions().then(function(qs) {
      renderQuestions(qs);
    });
  }

  function renderQuestions(qs) {
    var list = document.getElementById('bpreg-list');
    var count = document.getElementById('bpreg-count');
    if (!list) return;
    if (count) count.textContent = qs.length;
    if (!qs.length) {
      list.innerHTML = '<div class="bpreg-empty">💬 Aún no hay preguntas. ¡Sé el primero en preguntar!</div>';
      return;
    }
    list.innerHTML = qs.map(function(q) {
      var fecha = q.created_at ? new Date(q.created_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' }) : '';
      var nombre = q.user_name || 'Lector';
      return '<div class="bpreg-item">' +
        '<p class="bpreg-item-q">' + escapeHtml(q.pregunta) + '</p>' +
        '<p class="bpreg-item-meta">' + escapeHtml(nombre) + ' · ' + fecha + '</p>' +
        (q.respuesta ? '<div class="bpreg-item-a">' + escapeHtml(q.respuesta) + '</div>' : '') +
        '</div>';
    }).join('');
  }

  function showMsg(id, text, type) {
    var el = document.getElementById(id);
    if (!el) return;
    el.textContent = text;
    el.className = 'bpreg-msg ' + (type || '');
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ── Init ──
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      insertWidget();
      renderWidget();
    });
  } else {
    insertWidget();
    renderWidget();
  }

})();
