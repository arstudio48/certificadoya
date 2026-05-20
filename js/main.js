/* ============================================================
   CERTIFICADOYA.ES — Lógica principal
   Presupuesto instantáneo + Conexión Supabase
   ============================================================ */

// ============================================================
// CONFIGURACIÓN — Cambiar cuando tengas credenciales de Supabase
// ============================================================
const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_MsDx5jVGtDAzoB3l3-8DiQ_BxWpChA0';

// ============================================================
// TABLA DE PRECIOS POR ZONA (fallback local)
// ============================================================
const PRECIOS_ZONA = {
  // Madrid
  '280': { min: 0.75, max: 1.20, ciudad: 'Madrid' },
  '281': { min: 0.60, max: 0.95, ciudad: 'Madrid periferia' },
  '282': { min: 0.60, max: 0.95, ciudad: 'Madrid periferia' },
  '283': { min: 0.60, max: 0.95, ciudad: 'Madrid periferia' },
  '284': { min: 0.55, max: 0.85, ciudad: 'Sierra de Madrid' },
  '285': { min: 0.55, max: 0.85, ciudad: 'Madrid este' },
  '286': { min: 0.55, max: 0.85, ciudad: 'Madrid sur' },
  '287': { min: 0.55, max: 0.80, ciudad: 'Madrid norte' },
  '288': { min: 0.55, max: 0.85, ciudad: 'Madrid corredor del Henares' },
  '289': { min: 0.55, max: 0.85, ciudad: 'Madrid sur' },

  // Asturias
  '330': { min: 0.55, max: 0.85, ciudad: 'Oviedo' },
  '331': { min: 0.50, max: 0.80, ciudad: 'Oviedo periferia' },
  '332': { min: 0.55, max: 0.90, ciudad: 'Gijón' },
  '333': { min: 0.50, max: 0.80, ciudad: 'Gijón periferia' },
  '334': { min: 0.50, max: 0.80, ciudad: 'Avilés' },
  '335': { min: 0.45, max: 0.75, ciudad: 'Asturias oriental' },
  '336': { min: 0.50, max: 0.80, ciudad: 'Asturias central' },
  '337': { min: 0.45, max: 0.70, ciudad: 'Asturias occidental' },
  '338': { min: 0.45, max: 0.70, ciudad: 'Asturias montaña' },
  '339': { min: 0.50, max: 0.80, ciudad: 'Asturias' },

  // Barcelona
  '080': { min: 0.80, max: 1.30, ciudad: 'Barcelona' },
  '081': { min: 0.65, max: 1.00, ciudad: 'Barcelona área metropolitana' },
  '082': { min: 0.60, max: 0.95, ciudad: 'Barcelona área metropolitana' },
  '083': { min: 0.60, max: 0.90, ciudad: 'Barcelona costa' },
  '084': { min: 0.55, max: 0.85, ciudad: 'Barcelona interior' },
  '085': { min: 0.55, max: 0.85, ciudad: 'Barcelona interior' },
  '086': { min: 0.50, max: 0.80, ciudad: 'Barcelona interior' },
  '087': { min: 0.55, max: 0.85, ciudad: 'Barcelona interior' },
  '088': { min: 0.55, max: 0.85, ciudad: 'Barcelona costa' },
  '089': { min: 0.65, max: 1.00, ciudad: 'Barcelona área metropolitana' },

  // Valencia
  '460': { min: 0.60, max: 0.95, ciudad: 'Valencia' },
  '461': { min: 0.55, max: 0.85, ciudad: 'Valencia periferia' },
  '462': { min: 0.50, max: 0.80, ciudad: 'Valencia interior' },
  '463': { min: 0.50, max: 0.80, ciudad: 'Valencia interior' },
  '464': { min: 0.55, max: 0.85, ciudad: 'Valencia costa' },
  '465': { min: 0.55, max: 0.85, ciudad: 'Valencia costa' },
  '466': { min: 0.50, max: 0.80, ciudad: 'Valencia interior' },
  '467': { min: 0.55, max: 0.85, ciudad: 'Valencia costa' },
  '468': { min: 0.50, max: 0.80, ciudad: 'Valencia interior' },
  '469': { min: 0.55, max: 0.85, ciudad: 'Valencia periferia' },

  // Sevilla
  '410': { min: 0.60, max: 0.90, ciudad: 'Sevilla' },
  '411': { min: 0.50, max: 0.80, ciudad: 'Sevilla periferia' },
  '412': { min: 0.50, max: 0.80, ciudad: 'Sevilla periferia' },
  '413': { min: 0.45, max: 0.75, ciudad: 'Sevilla interior' },
  '414': { min: 0.45, max: 0.75, ciudad: 'Sevilla interior' },
  '415': { min: 0.50, max: 0.80, ciudad: 'Sevilla interior' },
  '416': { min: 0.50, max: 0.80, ciudad: 'Sevilla interior' },
  '417': { min: 0.50, max: 0.80, ciudad: 'Sevilla interior' },
  '418': { min: 0.45, max: 0.75, ciudad: 'Sevilla interior' },
  '419': { min: 0.50, max: 0.80, ciudad: 'Sevilla periferia' },
};

// Precio por defecto para el resto de España
const PRECIO_DEFAULT = { min: 0.45, max: 0.85 };

// ============================================================
// OBTENER PRECIO POR CÓDIGO POSTAL
// ============================================================
function obtenerPrecioZona(cp) {
  // Buscar por prefijo de 3 dígitos
  const prefijo = cp.substring(0, 3);
  const zona = PRECIOS_ZONA[prefijo];
  if (zona) {
    return { ...zona, cp };
  }
  // Si no está, usar precio nacional por defecto
  return { ...PRECIO_DEFAULT, cp, ciudad: 'tu zona' };
}

// ============================================================
// CALCULAR PRESUPUESTO (función llamada desde el botón)
// ============================================================
function calcularPresupuesto() {
  const cpInput = document.getElementById('cp');
  const m2Input = document.getElementById('m2');
  const resultadoBox = document.getElementById('resultado');
  const precioRango = document.getElementById('precio-rango');
  const precioTexto = document.getElementById('precio-texto');

  // Validar código postal
  const cp = cpInput.value.trim();
  if (!/^\d{5}$/.test(cp)) {
    alert('Por favor, introduce un código postal válido de 5 dígitos');
    cpInput.focus();
    return;
  }

  // Validar metros cuadrados
  const m2 = parseFloat(m2Input.value);
  if (!m2 || m2 < 20 || m2 > 5000) {
    alert('Por favor, introduce los metros cuadrados (mín. 20 m²)');
    m2Input.focus();
    return;
  }

  // Obtener precio de la zona
  const zona = obtenerPrecioZona(cp);
  const precioMin = Math.round(m2 * zona.min);
  const precioMax = Math.round(m2 * zona.max);

  // Mostrar resultado
  precioRango.textContent = `${precioMin}€ – ${precioMax}€`;
  precioTexto.textContent = `Precio estimado para ${zona.ciudad} (${m2} m²). El técnico te dará el precio exacto tras evaluar tu inmueble.`;
  resultadoBox.classList.add('visible');

  // Scroll suave al resultado
  resultadoBox.scrollIntoView({ behavior: 'smooth', block: 'center' });

  // Guardar datos para el lead
  window._presupuesto = { cp, m2, precioMin, precioMax, zona: zona.ciudad };
}

// ============================================================
// SOLICITAR LEAD (mostrar formulario modal)
// ============================================================
function solicitarLead() {
  const presupuesto = window._presupuesto;
  if (!presupuesto) {
    document.getElementById('presupuesto-card').scrollIntoView({ behavior: 'smooth' });
    return;
  }

  window._tipoInmueble = document.getElementById('tipo').value;
  document.getElementById('lead-modal').classList.add('visible');
  document.getElementById('lead-nombre').focus();
}

// CERRAR MODAL
function cerrarLeadModal() {
  document.getElementById('lead-modal').classList.remove('visible');
}

// CONFIRMAR LEAD (enviar a Supabase)
async function confirmarLead() {
  const presupuesto = window._presupuesto;
  const nombre = document.getElementById('lead-nombre').value.trim();
  const telefono = document.getElementById('lead-telefono').value.trim();

  if (!nombre || !telefono) {
    alert('Por favor, indica tu nombre y teléfono.');
    return;
  }

  const email = document.getElementById('lead-email').value.trim() || null;
  const btn = document.getElementById('lead-btn');
  btn.textContent = '⏳ Enviando...';
  btn.disabled = true;

  const lead = {
    nombre_cliente: nombre,
    telefono_cliente: telefono,
    email_cliente: email,
    codigo_postal: presupuesto.cp,
    ciudad: presupuesto.zona,
    m2: presupuesto.m2,
    tipo_inmueble: window._tipoInmueble,
    presupuesto_min: presupuesto.precioMin,
    presupuesto_max: presupuesto.precioMax,
    estado: 'nuevo',
    fuente: 'web'
  };

  // Guardar local
  const leads = JSON.parse(localStorage.getItem('leads') || '[]');
  leads.push({...lead, created_at: new Date().toISOString()});
  localStorage.setItem('leads', JSON.stringify(leads));

  // Enviar a Supabase
  let enviado = false;
  try {
    if (!window.supabase) {
      const { createClient } = await import('https://esm.sh/@supabase/supabase-js@2');
      window.supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    }
    const { error } = await window.supabase.from('leads').insert([lead]);
    if (error) {
      console.error('Supabase error:', error);
    } else {
      enviado = true;
    }
  } catch (err) {
    console.error('Error Supabase:', err);
  }

  // Cerrar modal y confirmar
  cerrarLeadModal();
  const icono = enviado ? '✅' : '📋';
  const extra = enviado ? '' : '\n\n(Guardado localmente — un administrador lo revisará pronto)';
  alert(`${icono} ¡Gracias ${nombre}!\n\nUn técnico de ${presupuesto.zona} te contactará en menos de 24h al ${telefono}.\n\nPresupuesto estimado: ${presupuesto.precioMin}€ – ${presupuesto.precioMax}€${extra}`);

  btn.textContent = 'Solicitar contacto';
  btn.disabled = false;
}

// ============================================================
// MODO TECNICO: Redirigir a página de registro
// ============================================================
if (window.location.pathname === '/tecnicos' || window.location.pathname === '/tecnicos/') {
  window.location.replace('/panel-tecnicos.html');
}

// ============================================================
// Exportar funciones globales
// ============================================================
window.calcularPresupuesto = calcularPresupuesto;
window.solicitarLead = solicitarLead;
window.confirmarLead = confirmarLead;
window.cerrarLeadModal = cerrarLeadModal;
window.registrarTecnico = registrarTecnico;

// ============================================================
// REGISTRAR TECNICO (formulario en /panel-tecnicos.html)
// ============================================================
async function registrarTecnico() {
  const nombre = document.getElementById('reg-nombre').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const telefono = document.getElementById('reg-telefono').value.trim();
  const titulacion = document.getElementById('reg-titulacion').value;
  const colegiado = document.getElementById('reg-colegiado').value.trim() || null;
  const provincias = document.getElementById('reg-provincias').value.trim();
  
  let cpRaw = document.getElementById('reg-cp').value.trim();
  // Parsear CPs (comas o saltos de línea)
  const cpCobertura = cpRaw.split(/[\n,]+/).map(s => s.trim()).filter(s => /^\d{2,3}$/.test(s));

  // Validar
  if (!nombre || !email || !telefono || !titulacion || !provincias) {
    alert('Por favor, completa todos los campos obligatorios.');
    return;
  }
  if (cpCobertura.length === 0) {
    alert('Indica al menos un código postal (prefijo de 3 dígitos).');
    return;
  }
  if (!/^\d{6,12}$/.test(telefono.replace(/\s/g,''))) {
    alert('Introduce un teléfono válido.');
    return;
  }

  const btn = document.getElementById('reg-btn');
  btn.textContent = '⏳ Enviando...';
  btn.disabled = true;

  try {
    if (!window.supabase) {
      const { createClient } = await import('https://esm.sh/@supabase/supabase-js@2');
      window.supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    }
    const { error } = await window.supabase.from('tecnicos').insert([{
      email, nombre, telefono, titulacion,
      numero_colegiado: colegiado,
      provincia: provincias,
      cp_cobertura: cpCobertura,
      verificado: false,
      activo: false
    }]);
    if (error) {
      if (error.code === '23505') {
        alert('Este email ya está registrado. Si crees que es un error, contáctanos.');
      } else {
        console.error('Error Supabase:', error);
        alert('Error al enviar la solicitud. Inténtalo de nuevo.');
      }
      btn.textContent = 'Enviar solicitud →';
      btn.disabled = false;
      return;
    }
    // Éxito
    document.getElementById('reg-form').style.display = 'none';
    document.getElementById('reg-exito').classList.add('visible');
    document.getElementById('reg-email-conf').textContent = email;
  } catch (err) {
    console.error('Error:', err);
    alert('Error de conexión. Inténtalo de nuevo.');
    btn.textContent = 'Enviar solicitud →';
    btn.disabled = false;
  }
}

console.log('⚡ CertificadoYa listo');
