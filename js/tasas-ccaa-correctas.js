// TASAS CCAA CORRECTAS (28 julio 2026)
// Sobrescribir TASA_REGISTRO con valores verificados
window.TASA_REGISTRO = {
  madrid: 0,
  asturias: 12.63,
  cantabria: 8.50,
  barcelona: 3.50,  // Cataluña
  galicia: 19.50,
  // Resto de CCAA sin tasa:
  alava: 0,
  albacete: 0,
  alicante: 0,
  almeria: 0,
  avila: 0,
  badajoz: 0,
  baleares: 0,
  burgos: 0,
  caceres: 0,
  cadiz: 0,
  castellon: 0,
  ceuta: 0,
  "ciudad-real": 0,
  cordoba: 0,
  "a-coruna": 0,
  cuenca: 0,
  gipuzkoa: 0,
  girona: 0,
  granada: 0,
  guadalajara: 0,
  huelva: 0,
  huesca: 0,
  jaen: 0,
  leon: 0,
  lleida: 0,
  lugo: 0,
  malaga: 0,
  melilla: 0,
  murcia: 0,
  navarra: 0,
  ourense: 0,
  palencia: 0,
  "las-palmas": 0,
  pontevedra: 0,
  "la-rioja": 0,
  salamanca: 0,
  segovia: 0,
  sevilla: 0,
  soria: 0,
  tarragona: 0,
  teruel: 0,
  toledo: 0,
  valencia: 0,
  valladolid: 0,
  bizkaia: 0,
  zamora: 0,
  zaragoza: 0,
  tenerife: 0,
  "santa-cruz-de-tenerife": 0
};

// Versión mejorada que muestra la tasa en el desglose y en el título
window.actualizarDesgloseConTasaMejorado = function(provinciaSlug) {
  const datos = window.PROVINCIA_TASAS_2026_COMPLETO?.[provinciaSlug];
  const desglose = document.getElementById('calc-resultado-desglose');
  
  if (!desglose || !datos) return;
  
  // Si hay tasa, agregarla al desglose visiblemente
  if (datos.tasa && datos.tasa > 0) {
    let html = desglose.innerHTML;
    
    // Eliminar línea anterior de tasa si existe
    html = html.replace(/<div class="desglose-linea"[^>]*><span><strong>Tasa [^<]*<\/strong><\/span>[\s\S]*?<\/div>/g, '');
    
    // Insertar nueva línea de tasa ANTES de "Total"
    const tasaHTML = `<div class="desglose-linea" style="border-top: 1px solid #e5e7eb; padding-top: 8px; margin-top: 8px;">
      <span><strong style="color: #16a34a;">Tasa de registro ${datos.ccaa}</strong></span>
      <span><strong style="color: #16a34a;">${datos.tasa.toFixed(2)} €</strong></span>
    </div>`;
    
    html = html.replace('<div class="desglose-linea-total">', tasaHTML + '<div class="desglose-linea-total">');
    desglose.innerHTML = html;
  }
};

console.log('✅ Tasas CCAA correctas cargadas (4 CCAA con tasa)');
