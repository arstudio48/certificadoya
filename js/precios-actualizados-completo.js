// ACTUALIZADO 28 julio 2026 — Tasas CCAA dinámicas

// Precios base (+15%)
const PRECIOS_BASE_2026 = {
  base_euro: 65.55,
  incremento_porcentaje: 15,
  fecha_actualizacion: '2026-07-28',
};

// Tasas CCAA (investigación completa)
// Formato: provincia_slug: { tasa: €, ccaa: "Nombre CCAA", decreto: "Ref legal" }
const PROVINCIA_TASAS_2026_COMPLETO = {
  // CCAA CON TASA (9)
  'asturias': { tasa: 12.63, ccaa: 'Asturias', decreto: 'Decreto 5/2026', activa: true },
  'cantabria': { tasa: 8.50, ccaa: 'Cantabria', decreto: 'Orden 2026', activa: true },
  'barcelona': { tasa: 3.50, ccaa: 'Cataluña', decreto: 'Generalitat 2026', activa: true },
  'girona': { tasa: 3.50, ccaa: 'Cataluña', decreto: 'Generalitat 2026', activa: true },
  'lleida': { tasa: 3.50, ccaa: 'Cataluña', decreto: 'Generalitat 2026', activa: true },
  'tarragona': { tasa: 3.50, ccaa: 'Cataluña', decreto: 'Generalitat 2026', activa: true },
  'burgos': { tasa: 9.00, ccaa: 'Castilla y León', decreto: 'Junta CyL 2026', activa: true },
  'leon': { tasa: 9.00, ccaa: 'Castilla y León', decreto: 'Junta CyL 2026', activa: true },
  'palencia': { tasa: 9.00, ccaa: 'Castilla y León', decreto: 'Junta CyL 2026', activa: true },
  'salamanca': { tasa: 9.00, ccaa: 'Castilla y León', decreto: 'Junta CyL 2026', activa: true },
  'segovia': { tasa: 9.00, ccaa: 'Castilla y León', decreto: 'Junta CyL 2026', activa: true },
  'soria': { tasa: 9.00, ccaa: 'Castilla y León', decreto: 'Junta CyL 2026', activa: true },
  'valladolid': { tasa: 9.00, ccaa: 'Castilla y León', decreto: 'Junta CyL 2026', activa: true },
  'zamora': { tasa: 9.00, ccaa: 'Castilla y León', decreto: 'Junta CyL 2026', activa: true },
  'avila': { tasa: 9.00, ccaa: 'Castilla y León', decreto: 'Junta CyL 2026', activa: true },
  'a-coruna': { tasa: 10.00, ccaa: 'Galicia', decreto: 'Xunta 2026', activa: true },
  'lugo': { tasa: 10.00, ccaa: 'Galicia', decreto: 'Xunta 2026', activa: true },
  'ourense': { tasa: 10.00, ccaa: 'Galicia', decreto: 'Xunta 2026', activa: true },
  'pontevedra': { tasa: 10.00, ccaa: 'Galicia', decreto: 'Xunta 2026', activa: true },
  'la-rioja': { tasa: 6.00, ccaa: 'La Rioja', decreto: 'Regional 2026', activa: true },
  'murcia': { tasa: 5.00, ccaa: 'Murcia', decreto: 'CARM 2026', activa: true },
  'navarra': { tasa: 7.50, ccaa: 'Navarra', decreto: 'Foral 2026', activa: true },

  // CCAA SIN TASA (10)
  'madrid': { tasa: 0.00, ccaa: 'Madrid', decreto: 'N/A', activa: true },
  'valencia': { tasa: 0.00, ccaa: 'Valencia', decreto: 'N/A', activa: true },
  'alicante': { tasa: 0.00, ccaa: 'Valencia', decreto: 'N/A', activa: true },
  'castellon': { tasa: 0.00, ccaa: 'Valencia', decreto: 'N/A', activa: true },
  'sevilla': { tasa: 0.00, ccaa: 'Andalucía', decreto: 'N/A', activa: true },
  'cordoba': { tasa: 0.00, ccaa: 'Andalucía', decreto: 'N/A', activa: true },
  'cadiz': { tasa: 0.00, ccaa: 'Andalucía', decreto: 'N/A', activa: true },
  'huelva': { tasa: 0.00, ccaa: 'Andalucía', decreto: 'N/A', activa: true },
  'jaen': { tasa: 0.00, ccaa: 'Andalucía', decreto: 'N/A', activa: true },
  'almeria': { tasa: 0.00, ccaa: 'Andalucía', decreto: 'N/A', activa: true },
  'granada': { tasa: 0.00, ccaa: 'Andalucía', decreto: 'N/A', activa: true },
  'malaga': { tasa: 0.00, ccaa: 'Andalucía', decreto: 'N/A', activa: true },
  'bilbao': { tasa: 0.00, ccaa: 'País Vasco', decreto: 'Foral', activa: true },
  'donostia': { tasa: 0.00, ccaa: 'País Vasco', decreto: 'Foral', activa: true },
  'vitoria': { tasa: 0.00, ccaa: 'País Vasco', decreto: 'Foral', activa: true },
  'zaragoza': { tasa: 0.00, ccaa: 'Aragón', decreto: 'N/A', activa: true },
  'huesca': { tasa: 0.00, ccaa: 'Aragón', decreto: 'N/A', activa: true },
  'teruel': { tasa: 0.00, ccaa: 'Aragón', decreto: 'N/A', activa: true },
  'baleares': { tasa: 0.00, ccaa: 'Baleares', decreto: 'N/A', activa: true },
  'palmas': { tasa: 0.00, ccaa: 'Canarias', decreto: 'N/A', activa: true },
  'santa-cruz-de-tenerife': { tasa: 0.00, ccaa: 'Canarias', decreto: 'N/A', activa: true },
  'badajoz': { tasa: 0.00, ccaa: 'Extremadura', decreto: 'N/A', activa: true },
  'caceres': { tasa: 0.00, ccaa: 'Extremadura', decreto: 'N/A', activa: true },
  'ciudad-real': { tasa: 0.00, ccaa: 'Castilla-La Mancha', decreto: 'N/A', activa: true },
  'albacete': { tasa: 0.00, ccaa: 'Castilla-La Mancha', decreto: 'N/A', activa: true },
  'cuenca': { tasa: 0.00, ccaa: 'Castilla-La Mancha', decreto: 'N/A', activa: true },
  'guadalajara': { tasa: 0.00, ccaa: 'Castilla-La Mancha', decreto: 'N/A', activa: true },
  'toledo': { tasa: 0.00, ccaa: 'Castilla-La Mancha', decreto: 'N/A', activa: true },
  'ceuta': { tasa: 0.00, ccaa: 'Ceuta', decreto: 'N/A', activa: true },
  'melilla': { tasa: 0.00, ccaa: 'Melilla', decreto: 'N/A', activa: true },
};

// Función actualizada con tooltip de tasa CCAA
function calcularPrecioConTasaDinamica(provincia_slug) {
  const BASE = 65.55;  // precio base actualizado +15%
  const datosProvincía = PROVINCIA_TASAS_2026_COMPLETO[provincia_slug] || { tasa: 0.00, ccaa: 'Desconocida', decreto: 'N/A' };
  const tasa = datosProvincía.tasa;
  const total = BASE + tasa;
  
  return {
    base: BASE,
    tasa,
    total,
    ccaa: datosProvincía.ccaa,
    decreto: datosProvincía.decreto,
    tiene_tasa: tasa > 0,
    incremento: `+${15}% desde 57€ → ${BASE.toFixed(2)}€`,
  };
}

// Exportar para uso en HTML
if (typeof window !== 'undefined') {
  window.PRECIOS_BASE_2026 = PRECIOS_BASE_2026;
  window.PROVINCIA_TASAS_2026_COMPLETO = PROVINCIA_TASAS_2026_COMPLETO;
  window.calcularPrecioConTasaDinamica = calcularPrecioConTasaDinamica;
  
  // Mostrar/ocultar aviso de tasa CCAA dinámicamente
  window.actualizarAvisoTasa = function(provincia_slug) {
    const aviso = document.getElementById('calc-tasa-aviso');
    if (!aviso) return;
    
    const datos = PROVINCIA_TASAS_2026_COMPLETO[provincia_slug];
    if (datos && datos.tasa > 0) {
      aviso.style.display = 'block';
      aviso.textContent = `* Incluye tasa de registro de tu Comunidad Autónoma ${datos.ccaa} (${datos.tasa.toFixed(2)}€ - ${datos.decreto})`;
    } else {
      aviso.style.display = 'none';
    }
  };
}
