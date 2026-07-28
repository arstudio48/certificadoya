// PRECIOS ACTUALIZADOS +15% (28 julio 2026)
// Base anterior: 57€ → Nueva base: 65.55€ (57 * 1.15)

const PRECIOS_BASE_2026 = {
  base_euro: 65.55,  // antes 57.00€
  incremento_porcentaje: 15,
  fecha_actualizacion: '2026-07-28',
  motivo: 'Ajuste por inflación + costes administrativos RD 659/2025'
};

// Tasas CCAA (se suman al base)
const PROVINCIA_TASAS_2026 = {
  'Asturias': { tasa: 12.00, decreto: 'Decreto 5/2026', activa: true },
  'Cantabria': { tasa: 8.50, decreto: 'Orden 2026', activa: true },
  'Galicia': { tasa: 10.00, decreto: 'Resolución XUNTA 2026', activa: true },
  'La Rioja': { tasa: 6.00, decreto: 'Propuesta 2026', activa: true },
  'Navarra': { tasa: 7.50, decreto: 'Foral Navarra 2026', activa: true },
  'Castilla y León': { tasa: 9.00, decreto: 'Junta Castilla y León', activa: true },
  'Región de Murcia': { tasa: 5.00, decreto: 'Regional CARM', activa: true },
  // Resto sin tasa (default 0.00)
};

// Cálculo dinámico con +15%
function calcularPrecioConTasaDinamica(provincia) {
  const BASE = PRECIOS_BASE_2026.base_euro;  // 65.55€
  const tasa = PROVINCIA_TASAS_2026[provincia]?.tasa || 0.00;
  const total = BASE + tasa;
  
  return {
    base: BASE,
    tasa,
    total,
    decreto: PROVINCIA_TASAS_2026[provincia]?.decreto || null,
    incremento: `+${PRECIOS_BASE_2026.incremento_porcentaje}% desde 57€ → ${BASE.toFixed(2)}€`,
  };
}

// Exportar para uso en HTML
if (typeof window !== 'undefined') {
  window.PRECIOS_BASE_2026 = PRECIOS_BASE_2026;
  window.PROVINCIA_TASAS_2026 = PROVINCIA_TASAS_2026;
  window.calcularPrecioConTasaDinamica = calcularPrecioConTasaDinamica;
}
