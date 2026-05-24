/* ============================================================
   CERTIFICADOYA.ES — Lógica principal
   Presupuesto instantáneo + Conexión Supabase
   ============================================================ */

// ============================================================
// CONFIGURACIÓN — Cambiar cuando tengas credenciales de Supabase
// ============================================================
const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_MsDx5jVGtDAzoB3l3-8DiQ_BxWpChA0';
const STRIPE_PUBLISHABLE_KEY = 'pk_test_51TaRD7Rty9TkFoA3itHdQj1A1TeYbK6b7XPIY8gbxAMOwUCjiEqjLhvkZb71IcsIge6b3b6cUUG319c7VWu0XdGl00jH3fl3dU';
//const SUPABASE_SERVICE_KEY = 'eliminado — se usa solo desde serverless functions';

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

// ============================================================
// MAPEO CP → PROVINCIA (para redirigir al calcular presupuesto)
// MAPEO CP → PROVINCIA (para redirigir al calcular presupuesto)
// Los primeros 2 dígitos del CP identifican la provincia
const CP_A_PROVINCIA = {
  '01': { slug: 'alava', nombre: 'Álava' },
  '02': { slug: 'albacete', nombre: 'Albacete' },
  '03': { slug: 'alicante', nombre: 'Alicante' },
  '04': { slug: 'almeria', nombre: 'Almería' },
  '05': { slug: 'avila', nombre: 'Ávila' },
  '06': { slug: 'badajoz', nombre: 'Badajoz' },
  '07': { slug: 'baleares', nombre: 'Baleares' },
  '08': { slug: 'barcelona', nombre: 'Barcelona' },
  '09': { slug: 'burgos', nombre: 'Burgos' },
  '10': { slug: 'caceres', nombre: 'Cáceres' },
  '11': { slug: 'cadiz', nombre: 'Cádiz' },
  '12': { slug: 'castellon', nombre: 'Castellón' },
  '13': { slug: 'ciudad-real', nombre: 'Ciudad Real' },
  '14': { slug: 'cordoba', nombre: 'Córdoba' },
  '15': { slug: 'a-coruna', nombre: 'A Coruña' },
  '16': { slug: 'cuenca', nombre: 'Cuenca' },
  '17': { slug: 'girona', nombre: 'Girona' },
  '18': { slug: 'granada', nombre: 'Granada' },
  '19': { slug: 'guadalajara', nombre: 'Guadalajara' },
  '20': { slug: 'gipuzkoa', nombre: 'Gipuzkoa' },
  '21': { slug: 'huelva', nombre: 'Huelva' },
  '22': { slug: 'huesca', nombre: 'Huesca' },
  '23': { slug: 'jaen', nombre: 'Jaén' },
  '24': { slug: 'leon', nombre: 'León' },
  '25': { slug: 'lleida', nombre: 'Lleida' },
  '26': { slug: 'la-rioja', nombre: 'La Rioja' },
  '27': { slug: 'lugo', nombre: 'Lugo' },
  '28': { slug: 'madrid', nombre: 'Madrid' },
  '29': { slug: 'malaga', nombre: 'Málaga' },
  '30': { slug: 'murcia', nombre: 'Murcia' },
  '31': { slug: 'navarra', nombre: 'Navarra' },
  '32': { slug: 'ourense', nombre: 'Ourense' },
  '33': { slug: 'asturias', nombre: 'Asturias' },
  '34': { slug: 'palencia', nombre: 'Palencia' },
  '35': { slug: 'las-palmas', nombre: 'Las Palmas' },
  '36': { slug: 'pontevedra', nombre: 'Pontevedra' },
  '37': { slug: 'salamanca', nombre: 'Salamanca' },
  '38': { slug: 'tenerife', nombre: 'Tenerife' },
  '39': { slug: 'cantabria', nombre: 'Cantabria' },
  '40': { slug: 'segovia', nombre: 'Segovia' },
  '41': { slug: 'sevilla', nombre: 'Sevilla' },
  '42': { slug: 'soria', nombre: 'Soria' },
  '43': { slug: 'tarragona', nombre: 'Tarragona' },
  '44': { slug: 'teruel', nombre: 'Teruel' },
  '45': { slug: 'toledo', nombre: 'Toledo' },
  '46': { slug: 'valencia', nombre: 'Valencia' },
  '47': { slug: 'valladolid', nombre: 'Valladolid' },
  '48': { slug: 'bizkaia', nombre: 'Bizkaia' },
  '49': { slug: 'zamora', nombre: 'Zamora' },
  '50': { slug: 'zaragoza', nombre: 'Zaragoza' },
  '51': { slug: 'ceuta', nombre: 'Ceuta' },
  '52': { slug: 'melilla', nombre: 'Melilla' },
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
// VALIDACIÓN VISUAL DEL FORMULARIO
// ============================================================
function validarCP() {
  const input = document.getElementById('cp');
  const error = document.getElementById('cp-error');
  const val = input.value.trim();
  if (val === '') { input.classList.remove('error'); error.textContent = ''; return; }
  if (!/^\d{5}$/.test(val)) {
    input.classList.add('error');
    error.textContent = 'El código postal debe tener 5 dígitos';
  } else {
    input.classList.remove('error');
    error.textContent = '';
  }
}

function validarM2() {
  const input = document.getElementById('m2');
  const error = document.getElementById('m2-error');
  const val = parseFloat(input.value);
  if (input.value === '') { input.classList.remove('error'); error.textContent = ''; return; }
  if (!val || val < 20) {
    input.classList.add('error');
    error.textContent = 'Mínimo 20 m²';
  } else if (val > 5000) {
    input.classList.add('error');
    error.textContent = 'Máximo 5.000 m²';
  } else {
    input.classList.remove('error');
    error.textContent = '';
  }
}

// ============================================================
// CALCULAR PRESUPUESTO (función llamada desde el botón)
// ============================================================
function calcularPresupuesto() {
  const cpInput = document.getElementById('cp');
  const m2Input = document.getElementById('m2');
  const tipoSelect = document.getElementById('tipo');
  const resultadoBox = document.getElementById('resultado');
  const precioRango = document.getElementById('precio-rango');
  const precioTexto = document.getElementById('precio-texto');

  // Validar código postal
  const cp = cpInput.value.trim();
  if (!/^\d{5}$/.test(cp)) {
    cpInput.classList.add('error');
    document.getElementById('cp-error').textContent = 'El código postal debe tener 5 dígitos';
    cpInput.focus();
    return;
  }

  // Validar metros cuadrados
  const m2 = parseFloat(m2Input.value);
  if (!m2 || m2 < 20 || m2 > 5000) {
    m2Input.classList.add('error');
    document.getElementById('m2-error').textContent = 'Introduce los m² (entre 20 y 5.000)';
    m2Input.focus();
    return;
  }

  // Obtener precio de la zona
  const zona = obtenerPrecioZona(cp);
  const precioMin = Math.round(m2 * zona.min);
  const precioMax = Math.round(m2 * zona.max);
  const tipo = tipoSelect ? tipoSelect.value : 'piso';

  // Mostrar resultado
  precioRango.textContent = `${precioMin}€ – ${precioMax}€`;
  precioTexto.textContent = `Precio estimado para ${zona.ciudad} (${m2} m², ${tipo}). El técnico te dará el precio exacto tras evaluar tu inmueble.`;
  
  resultadoBox.classList.add('visible');
  resultadoBox.scrollIntoView({ behavior: 'smooth', block: 'center' });

  // Guardar datos para el lead
  window._presupuesto = { cp, m2, precioMin, precioMax, zona: zona.ciudad, tipo: tipo };
}

// ============================================================
// SOLICITAR LEAD → REDIRIGIR A PÁGINA DE PROVINCIA
// ============================================================
function solicitarLead() {
  const presupuesto = window._presupuesto;
  if (!presupuesto) {
    document.getElementById('presupuesto-card').scrollIntoView({ behavior: 'smooth' });
    return;
  }

  // Obtener provincia del código postal
  const cpPrefix = presupuesto.cp.substring(0, 2);
  const provincia = CP_A_PROVINCIA[cpPrefix];
  
  if (provincia) {
    // Redirigir a la página de provincia con datos en la URL
    const params = new URLSearchParams({
      cp: presupuesto.cp,
      m2: presupuesto.m2,
      tipo: presupuesto.tipo || 'piso',
      min: presupuesto.precioMin,
      max: presupuesto.precioMax
    });
    window.location.href = `/certificado-energetico-${provincia.slug}/?${params.toString()}`;
  } else {
    // Si no encontramos la provincia, mostrar modal
    window._tipoInmueble = document.getElementById('tipo').value;
    document.getElementById('lead-modal').classList.add('visible');
    document.getElementById('lead-nombre').focus();
  }
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
    zona: presupuesto.zona,
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
window.validarCP = validarCP;
window.validarM2 = validarM2;
window.registrarTecnico = registrarTecnico;

// ============================================================
// REGISTRAR TECNICO (formulario en /panel-tecnicos.html)
// ============================================================
async function registrarTecnico() {
  const nombre = document.getElementById('reg-nombre').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const telefono = document.getElementById('reg-telefono').value.trim();
  const titulacion = document.getElementById('reg-titulacion').value;

  // Validar
  if (!nombre || !email || !telefono || !titulacion) {
    alert('Por favor, completa todos los campos.');
    return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    alert('Introduce un email válido.');
    return;
  }
  if (!/^\d{9}$/.test(telefono.replace(/\s/g, ''))) {
    alert('Introduce un teléfono válido (9 dígitos).');
    return;
  }

  const btn = document.getElementById('reg-btn');
  const originalText = btn.textContent;
  btn.textContent = '⏳ Enviando...';
  btn.disabled = true;

  try {
    const res = await fetch('/.netlify/functions/registro-tecnico', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre, email, telefono, titulacion })
    });

    const data = await res.json();

    if (!res.ok) {
      if (res.status === 409) {
        alert('Este email ya está registrado. Si crees que es un error, contáctanos.');
      } else {
        alert(data.error || 'Error al registrar. Inténtalo de nuevo.');
      }
      btn.textContent = originalText;
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
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

console.log('⚡ CertificadoYa listo');

/* ====== COOKIE CONSENT ====== */
window.aceptarCookies = function() {
  localStorage.setItem('cookie-consent', 'all');
  document.getElementById('cookie-banner').style.display = 'none';
};
window.rechazarCookies = function() {
  localStorage.setItem('cookie-consent', 'essential');
  document.getElementById('cookie-banner').style.display = 'none';
};
document.addEventListener('DOMContentLoaded', function() {
  if (localStorage.getItem('cookie-consent')) {
    document.getElementById('cookie-banner').style.display = 'none';
  }
});
