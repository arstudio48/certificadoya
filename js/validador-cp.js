/**
 * Validador de Código Postal — CertificadoYa
 * Valida CPs españoles en tiempo real, muestra cobertura por provincia,
 * bloquea el botón de calcular si el CP no es válido, y autocompleta la provincia.
 *
 * Uso: <script src="/js/validador-cp.js"></script> (después de main.js)
 * Compatible con el formulario de presupuesto existente (#cp, #cp-error, .btn-cta).
 */

// ============================================================
// MAPEO CP → PROVINCIA (prefijos de 2 dígitos, inline sin fetch)
// ============================================================
const CP_PROVINCIAS = {
  "01": "Álava",
  "02": "Albacete",
  "03": "Alicante",
  "04": "Almería",
  "05": "Ávila",
  "06": "Badajoz",
  "07": "Baleares",
  "08": "Barcelona",
  "09": "Burgos",
  "10": "Cáceres",
  "11": "Cádiz",
  "12": "Castellón",
  "13": "Ciudad Real",
  "14": "Córdoba",
  "15": "A Coruña",
  "16": "Cuenca",
  "17": "Girona",
  "18": "Granada",
  "19": "Guadalajara",
  "20": "Gipuzkoa",
  "21": "Huelva",
  "22": "Huesca",
  "23": "Jaén",
  "24": "León",
  "25": "Lleida",
  "26": "La Rioja",
  "27": "Lugo",
  "28": "Madrid",
  "29": "Málaga",
  "30": "Murcia",
  "31": "Navarra",
  "32": "Ourense",
  "33": "Asturias",
  "34": "Palencia",
  "35": "Las Palmas",
  "36": "Pontevedra",
  "37": "Salamanca",
  "38": "Santa Cruz de Tenerife",
  "39": "Cantabria",
  "40": "Segovia",
  "41": "Sevilla",
  "42": "Soria",
  "43": "Tarragona",
  "44": "Teruel",
  "45": "Toledo",
  "46": "Valencia",
  "47": "Valladolid",
  "48": "Bizkaia",
  "49": "Zamora",
  "50": "Zaragoza",
  "51": "Ceuta",
  "52": "Melilla"
};

// ============================================================
// INICIALIZACIÓN DEL VALIDADOR
// ============================================================
(function inicializarValidadorCP() {
  'use strict';

  function init() {
    // Buscar elementos del formulario
    var campoCP = document.getElementById('cp');
    if (!campoCP) return; // No hay formulario de CP en esta página

    var spanError = document.getElementById('cp-error');
    var botonCalcular = document.querySelector('.presupuesto-card-v2 .btn-cta');

    // Crear contenedor para el mensaje de cobertura/provincia
    var contenedorProvincia = document.getElementById('cp-provincia');
    if (!contenedorProvincia) {
      contenedorProvincia = document.createElement('div');
      contenedorProvincia.id = 'cp-provincia';
      contenedorProvincia.style.cssText = 'margin-top:6px;font-size:13px;font-weight:600;min-height:20px;transition:color .2s;font-family:Outfit,system-ui,sans-serif';
      // Insertar después del span de error
      if (spanError && spanError.parentNode) {
        spanError.parentNode.insertBefore(contenedorProvincia, spanError.nextSibling);
      } else {
        campoCP.parentNode.insertBefore(contenedorProvincia, campoCP.nextSibling);
      }
    }

    // Estado de validez del CP (para que otros scripts puedan consultarlo)
    window._cpValido = false;

    /**
     * Validar CP — se ejecuta en cada input del campo
     */
    function validarCPCobertura() {
      var cp = campoCP.value.trim();

      // Si está vacío, limpiar todo
      if (cp.length === 0) {
        campoCP.classList.remove('error');
        if (spanError) spanError.textContent = '';
        contenedorProvincia.textContent = '';
        contenedorProvincia.style.color = '';
        window._cpValido = false;
        desbloquearBoton();
        return;
      }

      // Si no tiene 5 dígitos aún, mostrar formato
      if (cp.length < 5 || !/^\d{5}$/.test(cp)) {
        // Solo mostrar error si tiene algún carácter
        if (cp.length > 0 && !/^\d+$/.test(cp)) {
          campoCP.classList.add('error');
          if (spanError) spanError.textContent = 'Solo números';
          contenedorProvincia.textContent = '';
          window._cpValido = false;
          bloquearBoton();
        } else if (cp.length === 5) {
          // Tiene 5 caracteres pero no son todos dígitos
          campoCP.classList.add('error');
          if (spanError) spanError.textContent = 'El código postal debe tener 5 dígitos';
          contenedorProvincia.textContent = '';
          window._cpValido = false;
          bloquearBoton();
        } else {
          // Aún escribiendo (menos de 5 dígitos), sin error
          campoCP.classList.remove('error');
          if (spanError) spanError.textContent = '';
          contenedorProvincia.textContent = '';
          contenedorProvincia.style.color = '';
          window._cpValido = false;
          desbloquearBoton();
        }
        return;
      }

      // Tenemos 5 dígitos — validar prefijo
      var prefijo = cp.substring(0, 2);
      var provincia = CP_PROVINCIAS[prefijo];

      if (provincia) {
        // ✅ CP VÁLIDO
        campoCP.classList.remove('error');
        if (spanError) spanError.textContent = '';
        contenedorProvincia.textContent = '\u2713 Cobertura en ' + provincia;
        contenedorProvincia.style.color = '#2e7d32';
        window._cpValido = true;
        desbloquearBoton();
      } else {
        // ❌ CP NO VÁLIDO
        campoCP.classList.add('error');
        if (spanError) spanError.textContent = '';
        contenedorProvincia.textContent = 'CP no válido, revisa el código';
        contenedorProvincia.style.color = '#d32f2f';
        window._cpValido = false;
        bloquearBoton();
      }
    }

    /**
     * Bloquear el botón "Calcular presupuesto"
     */
    function bloquearBoton() {
      if (!botonCalcular) return;
      botonCalcular.disabled = true;
      botonCalcular.style.opacity = '0.5';
      botonCalcular.style.cursor = 'not-allowed';
      botonCalcular.title = 'Introduce un código postal válido';
    }

    /**
     * Desbloquear el botón "Calcular presupuesto"
     */
    function desbloquearBoton() {
      if (!botonCalcular) return;
      botonCalcular.disabled = false;
      botonCalcular.style.opacity = '';
      botonCalcular.style.cursor = '';
      botonCalcular.title = '';
    }

    // Escuchar cambios en el campo CP
    campoCP.addEventListener('input', validarCPCobertura);
    campoCP.addEventListener('blur', validarCPCobertura);

    // Sobreescribir la función global validarCP para que incluya la cobertura
    window.validarCP = validarCPCobertura;

    // Validar al cargar si ya hay un valor (ej: autocompletado del navegador)
    if (campoCP.value) {
      validarCPCobertura();
    }
  }

  // Ejecutar cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
