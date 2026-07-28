// Overlay para asegurar que la tasa CCAA se muestra en el desglose
document.addEventListener('DOMContentLoaded', function() {
  // Cuando se calcula el precio, inyectar la tasa en el desglose
  const calcularPrecioOriginal = window.calcularPrecioF1;
  
  window.calcularPrecioF1 = function() {
    // Llamar función original
    calcularPrecioOriginal();
    
    // Después de calcular, actualizar desglose para mostrar tasa
    const provincia = document.getElementById('calc-provincia')?.value || '';
    const desglose = document.getElementById('calc-resultado-desglose');
    
    if (desglose && provincia) {
      // Obtener datos de tasa
      const tasaData = PROVINCIA_TASAS_2026_COMPLETO[provincia];
      
      if (tasaData && tasaData.tasa > 0) {
        // Inyectar línea de tasa en el desglose
        const tasaHTML = `<div class="desglose-linea" style="color: #16a34a; font-weight: 600;">
          <span>Tasa de registro ${tasaData.ccaa}</span>
          <span>${tasaData.tasa.toFixed(2)} €</span>
        </div>`;
        
        // Encontrar la línea "Total" e insertar antes
        const totalLine = desglose.querySelector('.desglose-linea-total');
        if (totalLine) {
          totalLine.insertAdjacentHTML('beforebegin', tasaHTML);
        } else {
          desglose.insertAdjacentHTML('beforeend', tasaHTML);
        }
      }
    }
  };
});
