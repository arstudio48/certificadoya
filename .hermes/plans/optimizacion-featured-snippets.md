# Plan de Optimización para Featured Snippets y Respuestas de IA
## Blog de CertificadoYa — Certificado de Eficiencia Energética (CEE)

**Fecha:** 26 de junio de 2026  
**Total artículos analizados:** 48 (excluyendo redirecciones y páginas de prueba)  
**Dominio:** certificadoya.es

---

## Diagnóstico General

| Indicador | Estado | % |
|---|---|---|
| FAQPage Schema (JSON-LD) presente | ✅ 47/48 | 98% |
| FAQ visible en página (h2 "Preguntas frecuentes") | ⚠️ ~24/48 | ~50% |
| FAQPage schema personalizado al tema del artículo | ❌ ~30/48 genéricos | 63% genéricos |
| Tablas con marcado semántico (<thead><th><tbody>) | ⚠️ 13/48 | 27% |
| Listas numeradas o con viñetas | ✅ 48/48 | 100% |
| Contenido responde "Qué/Cómo/Cuánto/Dónde" | ✅ 48/48 | 100% |

---

## Listado Completo de Artículos

### Leyenda
- **FAQ Schema**: ✅ Tiene FAQPage JSON-LD / ❌ No tiene
- **FAQ Visible**: ✅ Sección FAQ visible en la página / ❌ No visible
- **FAQ Match**: ✅ Las preguntas del schema coinciden con el tema del artículo / ❌ Son genéricas
- **Tabla Semántica**: ✅ Tabla con <thead><th><tbody> / ❌ Sin tabla o tabla no semántica
- **Prioridad**: 🔴 Alta / 🟡 Media / 🟢 Baja

---

### 1. ¿Qué es el certificado energético? (Guía Completa)
**Archivo:** `que-es-certificado-energetico.html`  
**Categoría:** Básico  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas detectados:**
- FAQPage schema usa preguntas genéricas (¿Qué es el CEE?, ¿Es obligatorio?) iguales en todos los artículos
- Sin tabla semántica (usa divs con clases)

**FAQ Schema sugerido (reemplazar el actual):**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Qué es el certificado energético (CEE)?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El Certificado de Eficiencia Energética (CEE) es un documento oficial que evalúa y califica la eficiencia energética de un inmueble con una letra de la A (muy eficiente) a la G (poco eficiente). Incluye consumo estimado de energía, emisiones de CO₂ y recomendaciones de mejora. Es obligatorio en España desde 2013."
      }
    },
    {
      "@type": "Question",
      "name": "¿Para qué sirve el certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Sirve para informar al comprador o inquilino sobre el consumo energético de la vivienda (una letra A puede gastar 10 veces menos que una G), fomentar la rehabilitación energética mediante recomendaciones de mejora, y cumplir con la normativa europea y española (Directiva 2010/31/UE y RD 390/2021)."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuándo es obligatorio el certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Es obligatorio para vender o alquilar cualquier vivienda, para obra nueva, edificios públicos de más de 250 m², y para solicitar subvenciones de rehabilitación. También debe aparecer la calificación en anuncios inmobiliarios. Ningún notario autorizará una compraventa sin el CEE vigente."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cómo se calcula el certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El técnico certificador visita el inmueble, mide las estancias, comprueba cerramientos y sistemas de climatización, e introduce los datos en programas oficiales como CE3X, HULC o CYPETHERM. El software calcula el consumo de energía primaria (kWh/m² año) y las emisiones de CO₂, asignando una letra de la A a la G."
      }
    }
  ]
}
```

**Frases/preguntas para capturar snippets:**
- "¿Qué es el certificado energético?" → Responder en párrafo inicial (ya lo hace)
- "¿Para qué sirve el certificado energético?" → Añadir párrafo introductorio que responda directamente
- "¿Cómo se calcula el certificado energético?" → El h2 y el ol (lista numerada) ya responden
- "¿Cuánto dura el certificado energético?" → Añadir respuesta destacada al inicio

---

### 2. Precio del Certificado Energético 2026: Tarifas por Provincia
**Archivo:** `precio-certificado-energetico-2026.html`  
**Categoría:** Precios  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ✅ 3 tablas semánticas | 🔴 Alta |

**Problemas detectados:**
- ❌ **No tiene FAQ visible** en la página (solo schema genérico)
- Las FAQ del schema son genéricas (¿Qué es el CEE?) en lugar de preguntas sobre precios

**FAQ Schema sugerido (específico del artículo):**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Cuánto cuesta un certificado energético en 2026?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El precio depende de los metros cuadrados, ubicación y tipo de inmueble. En 2026 los rangos son: piso pequeño (30-60 m²): 45-95 €; piso mediano (61-100 m²): 55-130 €; unifamiliar (120-300 m²): 120-280 €. Madrid y Barcelona son las más caras (60-280 €); Asturias y zonas rurales las más económicas (desde 45 €)."
      }
    },
    {
      "@type": "Question",
      "name": "¿Por qué varía el precio del certificado energético por provincia?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Varía por tres razones principales: el coste de vida y honorarios profesionales de cada zona (un técnico en Madrid cobra más que en zona rural), la densidad de técnicos disponibles (más competencia = precios más bajos), y los desplazamientos (zonas remotas pueden tener sobrecoste)."
      }
    },
    {
      "@type": "Question",
      "name": "¿Qué incluye el precio del certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El precio debe incluir: visita del técnico al inmueble con mediciones reales, emisión del certificado mediante software oficial (CE3X, HULC o CYPETHERM), y registro en el órgano autonómico correspondiente. Sin registro, el certificado no tiene validez legal."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuánto cuesta un certificado energético en Madrid en 2026?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Madrid es la provincia más cara de España. Un piso de 80 m² cuesta entre 75-120 € en la capital, y entre 55-95 € en la periferia (Alcorcón, Leganés, Getafe). En zonas prime como Salamanca o Chamberí puede alcanzar los 155 €. La media es un 15-25 % más alta que la media nacional."
      }
    }
  ]
}
```

**Frases/preguntas para capturar snippets:**
- "¿Cuánto cuesta un certificado energético en 2026?" → Ya responde en el primer párrafo, reforzar
- "¿Cuánto cuesta un certificado energético en Madrid/Barcelona/Valencia?" → Ya hay tablas desglosadas
- "¿Qué incluye el precio del certificado energético?" → Añadir respuesta directa destacada
- "¿Por qué varía el precio del certificado energético?" → Callout existente, mover a posición más temprana

**Acciones:** Añadir sección FAQ visible con estas preguntas al final del artículo

---

### 3. Certificado Energético Obligatorio 2026: Multas hasta 6.000€
**Archivo:** `certificado-energetico-obligatorio-2026.html`  
**Categoría:** Normativa  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ❌ Parcial | ✅ 2 tablas semánticas | 🟡 Media |

**Problemas detectados:**
- FAQ visible existe pero usa preguntas solo parcialmente alineadas
- El FAQ schema podría ser más específico sobre obligatoriedad

**FAQ Schema sugerido (optimizado):**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Sigue siendo obligatorio el certificado energético en 2026?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Sí, el certificado de eficiencia energética (CEE) sigue siendo obligatorio en toda España desde el 1 de junio de 2013. No hay ninguna modificación legislativa que lo haya eliminado. Es exigible para vender, alquilar, obra nueva y edificios públicos. Las sanciones por no tenerlo siguen vigentes y se aplican."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuánto es la multa por no tener el certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Las sanciones van de 300 € a 6.000 € según la gravedad: infracciones leves (300-1.000 €) por no tener el CEE en venta o alquiler, graves (1.001-2.000 €) por falsear datos, y muy graves (2.001-6.000 €) por reincidencia o fraude. Además, el notario puede bloquear la operación inmobiliaria."
      }
    },
    {
      "@type": "Question",
      "name": "¿Qué normativa regula el certificado energético en España?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "La normativa principal es el Real Decreto 390/2021, que transpone la Directiva 2010/31/UE de la Unión Europea. También complementan el Código Técnico de la Edificación (CTE DB-HE) y las leyes autonómicas. Cada comunidad autónoma tiene su propio registro de certificados."
      }
    },
    {
      "@type": "Question",
      "name": "¿Qué viviendas están exentas del certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Están exentas: edificios protegidos por valor arquitectónico, monumentos, lugares de culto, inmuebles industriales sin demanda energética, viviendas de temporada usadas menos de 4 meses al año, y edificios independientes con superficie útil inferior a 50 m². Los pisos en bloques no están exentos aunque tengan menos de 50 m²."
      }
    }
  ]
}
```

**Frases/preguntas para capturar snippets:**
- "¿Es obligatorio el certificado energético en 2026?" → Ya lo responde al inicio, mantener
- "¿Cuánto es la multa por no tener el CEE?" → Tabla semántica ya existe, buena para snippet
- "¿Qué normativa regula el certificado energético?" → Añadir respuesta destacada tipo callout
- "¿Qué viviendas están exentas del certificado energético?" → Lista con viñetas ya existe ✅

---

### 4. Certificado Energético para Alquilar: Guía Completa para Caseros
**Archivo:** `certificado-energetico-alquiler.html`  
**Categoría:** Alquiler  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🔴 Alta |

**Problemas detectados:**
- ❌ **No tiene FAQ visible** en la página
- FAQ schema con preguntas genéricas no relacionadas con alquiler
- ❌ Sin tabla semántica

**FAQ Schema sugerido (específico del artículo):**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Es obligatorio el certificado energético para alquilar en 2026?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Sí, sin excepciones para el 99% de los casos. El Real Decreto 235/2013, actualizado por el RD 390/2021, establece que todo inmueble que se alquile debe disponer de un certificado energético vigente. Da igual si alquilas por un mes o por diez años: el certificado es obligatorio. Las únicas excepciones son edificios protegidos, lugares de culto, viviendas de uso inferior a 4 meses al año y construcciones provisionales de menos de 2 años."
      }
    },
    {
      "@type": "Question",
      "name": "¿Qué pasa si alquilo sin certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Alquilar sin CEE puede salirte caro. Las sanciones van de 300 € a 6.000 € según la gravedad. Además, el inquilino podría exigir la resolución del contrato por incumplimiento. En plataformas como Idealista o Fotocasa es obligatorio mostrar la letra del CEE en el anuncio. Sin ella, el anuncio puede ser rechazado."
      }
    },
    {
      "@type": "Question",
      "name": "¿Quién paga el certificado energético, el casero o el inquilino?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El certificado energético siempre lo paga el propietario. Es un documento vinculado al inmueble, no al inquilino. El precio depende de los m² y la zona, pero para una vivienda tipo de 70-80 m² en capital ronda los 60-120 €. El casero debe tenerlo antes de publicar el anuncio de alquiler."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuánto dura el certificado energético para alquiler?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El CEE tiene una validez de 10 años. Si la vivienda ya tenía uno, comprueba la fecha de emisión. Si está caducado, necesitas uno nuevo. Si hiciste reformas importantes (cambio de ventanas, aislamiento, caldera), el certificado anterior ya no es válido y debes obtener uno nuevo que refleje las mejoras."
      }
    }
  ]
}
```

**Frases/preguntas para capturar snippets:**
- "¿Es obligatorio el certificado energético para alquilar?" → Ya está en h2, reforzar
- "¿Qué pasa si alquilo sin certificado energético?" → Añadir sección FAQ visible
- "¿Quién paga el certificado energético en un alquiler?" → Ya responde, destacar más
- "¿Cuánto dura el certificado energético para alquilar?" → Ya hay h2, mantener

**Acciones:** Añadir sección FAQ visible al final del artículo con 4 preguntas sobre alquiler

---

### 5. Sanciones por no tener el Certificado Energético 2026
**Archivo:** `sanciones-certificado-energetico-2026.html`  
**Categoría:** Legal  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ 1 tabla semántica | 🟢 Baja |

**Problemas detectados:**
- Buen estado general. FAQ visible y schema están alineados al tema de sanciones ✅
- La tabla de sanciones es semántica ✅
- Las preguntas del FAQ son específicas ✅

**Mejoras sugeridas:**
- Añadir una pregunta sobre "¿Cuánto tardan en caducar las sanciones?" (lo menciona en texto)
- Mejorar snippet potencial: "¿Cuánto es la multa por no tener el certificado energético?"

**FAQ Schema adicional (preguntas extra):**
```json
{
  "@type": "Question",
  "name": "¿Las sanciones del certificado energético prescriben?",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "Sí. Las infracciones leves prescriben a los 6 meses, las graves al año y las muy graves a los 2 años desde que se cometieron. Sin embargo, el plazo se reinicia si la administración realiza algún acto de investigación o notificación."
  }
}
```

---

### 6. Caducidad del Certificado Energético
**Archivo:** `caducidad-certificado-energetico.html`  
**Categoría:** Básico  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ❌ **No coincide** | ❌ Sin tabla | 🔴 Alta |

**Problemas detectados:**
- ❌ **FAQPage schema tiene preguntas sobre "ayudas y subvenciones"** que NO corresponden al tema del artículo (caducidad del CEE). Es un error grave de topical matching.
- FAQ visible sí habla de caducidad, pero el schema JSON-LD está completamente desalineado

**FAQ Schema CORREGIDO (específico del artículo):**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Cuánto dura el certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El certificado de eficiencia energética (CEE) tiene una validez máxima de 10 años desde su fecha de emisión, según el artículo 12 del Real Decreto 390/2021. Para edificios públicos de más de 250 m², la validez es de 5 años."
      }
    },
    {
      "@type": "Question",
      "name": "¿Qué pasa si uso un certificado energético caducado?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Usar un CEE caducado equivale a no tener certificado. El notario no autorizará la escritura de compraventa, el inquilino puede denunciarte, te expones a sanciones de 300 a 6.000 €, y las subvenciones de rehabilitación serán denegadas. El certificado caducado no tiene ningún efecto legal."
      }
    },
    {
      "@type": "Question",
      "name": "¿Se puede renovar el certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Sí. Cuando un certificado caduca, puedes solicitar uno nuevo. Técnicamente no existe la 'renovación' como tal: el proceso es idéntico al inicial. El técnico visita el inmueble, toma datos y emite un nuevo CEE con validez de otros 10 años. Si has realizado mejoras energéticas, tu calificación podría mejorar."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuándo empieza a contar la caducidad del certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "La fecha de caducidad se cuenta desde la fecha de emisión del certificado, no desde la fecha de inspección ni desde la fecha de registro en la comunidad autónoma. El plazo de 10 años empieza cuando el técnico firma y emite el documento."
      }
    }
  ]
}
```

**Frases/preguntas para capturar snippets:**
- "¿Cuánto dura el certificado energético?" → Responder en primer párrafo
- "¿Qué pasa si uso un certificado energético caducado?" → Añadir respuesta destacada
- "¿Se puede renovar el certificado energético?" → Ya hay h2
- "¿Cuándo caduca el certificado energético?" → Añadir snippet temprano

---

### 7. Mejorar Eficiencia Energética de tu Vivienda
**Archivo:** `mejorar-eficiencia-energetica-vivienda.html`  
**Categoría:** Mejoras  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ✅ 1 tabla semántica | 🔴 Alta |

**Problemas detectados:**
- ❌ **No tiene FAQ visible** en la página
- FAQ schema genérico en lugar de preguntas sobre mejoras energéticas

**FAQ Schema sugerido (específico del artículo):**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Cómo puedo mejorar la letra de mi certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Las mejoras más efectivas son: aislamiento térmico de fachadas y cubiertas (reduce la demanda 40-60%), cambio de ventanas a PVC con doble acristalamiento, instalación de aerotermia en lugar de caldera de gas, placas solares fotovoltaicas, iluminación LED, y electrodomésticos clase A+++. La combinación puede subir la letra de E a B o incluso A."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuánto cuesta mejorar la eficiencia energética de una vivienda?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Depende de las mejoras: aislar fachada puede costar entre 8.000-15.000 €, cambiar ventanas 4.000-8.000 €, instalar aerotermia 7.000-12.000 €, y placas solares 5.000-8.000 €. Existen ayudas Next Generation de hasta 21.400 € y deducciones en el IRPF de hasta el 60% por obras de mejora energética."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuánto se puede ahorrar mejorando la eficiencia energética?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Una vivienda con letra A puede ahorrar hasta un 90% en la factura energética respecto a una letra G. En términos económicos, pasar de letra E a B puede suponer un ahorro de 500-800 € anuales en calefacción y electricidad. La inversión en mejoras se amortiza típicamente en 5-10 años."
      }
    },
    {
      "@type": "Question",
      "name": "¿Qué subvenciones existen para mejorar la eficiencia energética en 2026?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "En 2026 existen ayudas Next Generation EU de hasta 21.400 € por vivienda para rehabilitación energética, deducciones en el IRPF de hasta el 60% por obras de mejora, y bonificaciones en el IBI en muchos municipios para viviendas con letra A o B. Cada comunidad autónoma gestiona sus propias convocatorias."
      }
    }
  ]
}
```

**Frases/preguntas para capturar snippets:**
- "¿Cómo mejorar la eficiencia energética de mi vivienda?" → El artículo es una lista numerada perfecta para snippet
- "¿Cuánto cuesta mejorar la eficiencia energética?" → Añadir respuesta destacada
- "¿Cuánto se ahorra mejorando la eficiencia energética?" → Ya hay datos en el texto
- "¿Qué subvenciones hay para mejorar la eficiencia?" → Ya lo menciona, reforzar

**Acciones:** Añadir sección FAQ visible al final del artículo

---

### 8. Certificado Energético Online
**Archivo:** `certificado-energetico-online.html`  
**Categoría:** Servicio  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ❌ Parcial | ❌ Sin tabla | 🟡 Media |

**Problemas detectados:**
- FAQ visible existe ✅
- FAQ schema genérico en lugar de preguntas sobre proceso online

**FAQ Schema específico sugerido:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Se puede obtener el certificado energético online?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Sí, puedes obtener el certificado energético online a través de plataformas como CertificadoYa. El proceso incluye: presupuesto instantáneo online, contacto con un técnico certificador de tu zona en 24h, visita al inmueble, y entrega del certificado registrado por email en 48-96h."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuánto cuesta el certificado energético online?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El precio del certificado energético online varía según metros y ubicación. En CertificadoYa los precios van desde 45 € para pisos pequeños hasta 250 € para viviendas unifamiliares grandes. El presupuesto es instantáneo y gratuito, sin compromiso."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuánto tarda el certificado energético online?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El proceso completo suele llevar 48-96 horas: presupuesto instantáneo (5 segundos), contacto del técnico (1-24h), visita al inmueble (48-96h), emisión y registro del certificado (48-96h tras la visita). En casos urgentes se puede acelerar a 48 horas."
      }
    },
    {
      "@type": "Question",
      "name": "¿El certificado energético online es legal y válido?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Sí, siempre que lo emita un técnico colegiado y se registre en el órgano autonómico correspondiente. La gestión online es solo la plataforma de contratación. La visita del técnico es presencial, el cálculo se hace con software oficial (CE3X, HULC) y el registro es oficial."
      }
    }
  ]
}
```

---

### 9. Certificado Energético para Vender Piso
**Archivo:** `certificado-energetico-vender-piso.html`  
**Categoría:** Venta  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ❌ Parcial | ❌ Sin tabla | 🟡 Media |

**Problemas detectados:**
- FAQ visible existe ✅
- FAQ schema podría ser más específico sobre venta

**FAQ Schema específico sugerido:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Es obligatorio el certificado energético para vender un piso en 2026?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Sí, el certificado energético es obligatorio para vender cualquier vivienda en España desde 2013. El notario exige el certificado original para autorizar la escritura de compraventa. Sin él, la venta se bloquea. Además, debes incluir la calificación energética en el anuncio de venta."
      }
    },
    {
      "@type": "Question",
      "name": "¿Qué precio tiene el certificado energético para vender un piso?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Para vender un piso, el certificado energético cuesta entre 45 € (piso pequeño en Asturias o zona rural) y 130 € (piso mediano en Madrid). En CertificadoYa el precio es desde 45 € con presupuesto instantáneo. El coste del certificado es muy inferior a las multas por no tenerlo."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuánto dura el certificado energético para vender?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El CEE tiene una validez de 10 años desde su emisión. Si está caducado, el notario rechazará la operación. Si caduca durante el proceso de venta, deberás renovarlo antes de firmar la escritura. Revisa la fecha de caducidad al iniciar el proceso de venta."
      }
    },
    {
      "@type": "Question",
      "name": "¿Puedo vender un piso sin certificado energético si el comprador acepta?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. La ley no permite eximir la obligación ni aunque ambas partes estén de acuerdo. Es una obligación imperativa: no se puede renunciar a ella ni pactar en contra. El notario exigirá el certificado para la escritura pública de compraventa."
      }
    }
  ]
}
```

---

### 10. Certificado Energético para Alquiler Vacacional
**Archivo:** `certificado-energetico-alquiler-vacacional.html`  
**Categoría:** Alquiler  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

**Problemas detectados:**
- Buen estado, FAQ visible alineada al tema ✅
- Tiene clase "faq" en HTML ✅
- Sección FAQ bien estructurada

**Mejora sugerida:** Solo ajustar FAQ schema para añadir una pregunta sobre exenciones

---

### 11. Garaje Trasero ¿Necesita Certificado Energético?
**Archivo:** `garaje-trasero-necesita-certificado-energetico.html`  
**Categoría:** Exenciones  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

**Problemas detectados:**
- Buen estado ✅
- Tiene clase "faq" en HTML ✅
- FAQ visible y schema alineados

---

### 12. Certificado Energético y Cédula de Habitabilidad
**Archivo:** `certificado-energetico-cedula-habitabilidad.html`  
**Categoría:** Comparativa  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ❌ Parcial | ❌ Sin tabla | 🟡 Media |

**Problemas detectados:**
- FAQ visible ✅ pero el schema es genérico
- Las preguntas del schema no diferencian entre CEE y cédula

**FAQ Schema específico sugerido:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Es lo mismo el certificado energético que la cédula de habitabilidad?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No, son documentos completamente distintos. La cédula de habitabilidad certifica que la vivienda cumple las condiciones mínimas para ser habitada (dimensiones, ventilación, salubridad). El certificado energético (CEE) evalúa exclusivamente la eficiencia energética del inmueble. Ambos son obligatorios para vender, pero los regula normativa diferente."
      }
    },
    {
      "@type": "Question",
      "name": "¿Se necesita el certificado energético para obtener la cédula de habitabilidad?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No, son trámites independientes. Puedes tener la cédula de habitabilidad sin tener el certificado energético y viceversa. Sin embargo, para vender una vivienda necesitas ambos documentos. Cada uno lo regula una normativa distinta y los solicitan organismos diferentes."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuánto cuesta la cédula de habitabilidad y el certificado energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El certificado energético cuesta entre 45-280 € según tamaño y ubicación. La cédula de habitabilidad tiene un coste variable según la comunidad autónoma, generalmente entre 50-150 € más tasas municipales. En total, ambos documentos pueden costar entre 100-400 €."
      }
    }
  ]
}
```

---

### 13. Certificado Energético Obra Nueva
**Archivo:** `certificado-energetico-obra-nueva.html`  
**Categoría:** Obra nueva  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** FAQ schema genérico en lugar de preguntas sobre obra nueva.

---

### 14. Certificado Energético Sin Visita
**Archivo:** `certificado-energetico-sin-visita.html`  
**Categoría:** Servicio  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ❌ Parcial | ✅ 1 tabla semántica | 🟡 Media |

**Problemas:** FAQ schema genérico, podría ser más específico sobre la modalidad sin visita.

---

### 15. Aerotermia y Certificado Energético
**Archivo:** `aerotermia-certificado-energetico.html`  
**Categoría:** Mejoras  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible, schema genérico.

---

### 16. Placas Solares y Certificado Energético
**Archivo:** `placas-solares-certificado-energetico.html`  
**Categoría:** Mejoras  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible, schema genérico.

---

### 17. Normativa de Certificación Energética en España
**Archivo:** `normativa-certificacion-energetica-espana.html`  
**Categoría:** Normativa  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible, schema genérico.

---

### 18. Directiva UE 2024/1275 Rehabilitación Obligatoria
**Archivo:** `directiva-ue-2024-1275-rehabilitacion-obligatoria.html`  
**Categoría:** Normativa  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ❌ Parcial | ❌ Sin tabla | 🟡 Media |

---

### 19. RD 659/2025: ¿Qué Cambia tu Certificado Energético?
**Archivo:** `rd-659-2025-que-cambia-tu-certificado-energetico.html`  
**Categoría:** Normativa  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ (×2 duplicado) | ✅ | ✅ | ❌ Sin tabla | 🟡 Media |

**Problema:** ⚠️ Tiene **dos FAQPage schema** duplicados (líneas 43 y 243). Eliminar uno.

---

### 20. Aprobado el RD 659/2025: FP Superior para Certificador
**Archivo:** `rd-659-2025-fp-superior-certificado-energetico.html`  
**Categoría:** Normativa  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 21. Reforma del Certificado Energético 2026: Cambios
**Archivo:** `reforma-certificado-energetico-2026-cambios.html`  
**Categoría:** Normativa  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ✅ 1 tabla semántica | 🟢 Baja |

---

### 22. Normativa CEE 2026
**Archivo:** `normativa-cee-2026.html`  
**Categoría:** Normativa  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 23. Precios por Provincia 2026
**Archivo:** `precios-certificado-energetico-provincias-2026.html`  
**Categoría:** Precios  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla semántica | 🔴 Alta |

**Problemas:**
- ❌ **No tiene FAQ visible**
- ❌ Las tablas NO son semánticas (CSS class `precios-table` sin `<thead>`/`<th>` semánticos)
- FAQ schema genérico

**Acción prioritaria:** Añadir tabla semántica y FAQ visible con preguntas sobre precios por provincia.

---

### 24. CEE e Hipoteca: ¿El Banco lo Exige?
**Archivo:** `cee-hipoteca-banco.html`  
**Categoría:** Financiero  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

---

### 25. Certificado Energético para Segunda Vivienda
**Archivo:** `certificado-energetico-segunda-vivienda.html`  
**Categoría:** Exenciones  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

---

### 26. Certificado Energético para Garajes y Locales
**Archivo:** `certificado-energetico-garajes-locales.html`  
**Categoría:** Exenciones  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ✅ 1 tabla semántica | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 27. Certificado Energético Locales Comerciales
**Archivo:** `certificado-energetico-locales-comerciales.html`  
**Categoría:** Exenciones  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 28. Certificado Energético Venta
**Archivo:** `certificado-energetico-venta.html`  
**Categoría:** Venta  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 29. Errores Comunes del CEE
**Archivo:** `errores-comunes-cee.html`  
**Categoría:** Técnicos  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 30. Cómo Darse de Alta como Técnico Certificador
**Archivo:** `como-darse-de-alta-tecnico-certificador.html`  
**Categoría:** Técnicos  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 31. Etiqueta Energética de Edificios
**Archivo:** `etiqueta-energetica-edificios.html`  
**Categoría:** Básico  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 32. Guía CE3X para Técnicos
**Archivo:** `guia-ce3x-tecnicos.html`  
**Categoría:** Técnicos  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

---

### 33. Guía CE3X Avanzada
**Archivo:** `guia-ce3x-avanzada.html`  
**Categoría:** Técnicos  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

---

### 34. HULC vs CE3X vs CYPETHERM
**Archivo:** `hulc-cype-vs-ce3x.html`  
**Categoría:** Técnicos  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 35. Guía Subvenciones Rehabilitación 2026
**Archivo:** `guia-subvenciones-rehabilitacion-energetica-2026.html`  
**Categoría:** Ayudas  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 36. Plan Social Clima: 9.099 Millones en Ayudas
**Archivo:** `plan-social-clima-9099-millones-ayudas.html`  
**Categoría:** Ayudas  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

---

### 37. Ayudas 21.400€ Rehabilitación 2026
**Archivo:** `ayudas-21400-euros-rehabilitacion-2026.html`  
**Categoría:** Ayudas  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

---

### 38. Subvenciones Rehabilitación 20.000€ (Plazo 30 Junio)
**Archivo:** `subvenciones-rehabilitacion-20mil-plazo-30-junio.html`  
**Categoría:** Ayudas  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

---

### 39. Últimos Días Ayudas 20.000€ Rehabilitación 2026
**Archivo:** `ultimos-dias-ayudas-20000-euros-rehabilitacion-2026.html`  
**Categoría:** Ayudas  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

---

### 40. Se Acaba el Dinero Europeo: Guía Comunidades de Vecinos
**Archivo:** `se-acaba-dinero-europeo-guia-comunidades-vecinos.html`  
**Categoría:** Ayudas  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

---

### 41. Obligación de Reformar Viviendas: Guía 2026-2030
**Archivo:** `obligacion-reformar-viviendas-guia-2026-2030.html`  
**Categoría:** Normativa  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ | ✅ | ❌ Sin tabla | 🟢 Baja |

---

### 42. Rehabilitación Energética de Edificios
**Archivo:** `rehabilitacion-energetica-edificios.html`  
**Categoría:** Rehabilitación  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 43. Registro CEE por Comunidades Autónomas
**Archivo:** `registro-cee-comunidades-autonomas.html`  
**Categoría:** Técnicos  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 44. Registro Centralizado de Técnicos Certificadores
**Archivo:** `registro-centralizado-tecnicos-certificadores.html`  
**Categoría:** Técnicos  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 45. VPO y Certificado Energético
**Archivo:** `vpo-certificado-energetico.html`  
**Categoría:** Exenciones  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 46. Vivienda Estándar en España: Medidas y Precio CEE
**Archivo:** `vivienda-estandar-espana-medidas-precio-cee.html`  
**Categoría:** Precios  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ❌ | ❌ Genérica | ❌ Sin tabla | 🟡 Media |

**Problemas:** ❌ No tiene FAQ visible.

---

### 47. Plantilla de Informe Energético para Técnicos
**Archivo:** `plantilla-informe-energetico.html`  
**Categoría:** Técnicos  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ❌ | ❌ | ❌ | ❌ Sin tabla | 🔴 Alta |

**Problemas detectados:**
- ❌ **No tiene FAQPage schema** (es el único artículo que carece de él)
- ❌ **No tiene FAQ visible**
- ❌ No responde preguntas del usuario (es una guía para técnicos, no FAQ-oriented)
- Solamente tiene Article y BlogPosting schema

**FAQ Schema necesario (añadir):**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Qué debe incluir un informe de certificación energética?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Un informe profesional debe incluir: portada con datos del inmueble, datos del técnico (nombre, titulación, nº colegiado), descripción del inmueble, calificación energética con letra A-G, etiqueta oficial, consumo en kWh/m² año, medidas de mejora con coste estimado y ahorro esperado, y anexos con fotografías y PDF generado por CE3X."
      }
    },
    {
      "@type": "Question",
      "name": "¿Qué datos del técnico deben aparecer en el informe?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Deben constar: nombre completo, titulación (arquitecto, aparejador, ingeniero), número de colegiado y colegio profesional, teléfono y email de contacto. Sin estos datos el informe no tiene validez legal."
      }
    },
    {
      "@type": "Question",
      "name": "¿Cuántas medidas de mejora debe incluir un informe energético?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El informe debe incluir al menos 2 medidas de mejora viables, cada una con su coste estimado y ahorro esperado. Las medidas pueden incluir aislamiento térmico, cambio de ventanas, instalación de aerotermia o placas solares, e iluminación LED."
      }
    }
  ]
}
```

**Frases/preguntas para capturar snippets:**
- "¿Qué debe incluir un informe de certificación energética?" → Ya hay estructura clara con listas
- "¿Qué datos del técnico deben aparecer?" → Lista en h2 "Datos del técnico"
- "¿Cuántas medidas de mejora debe incluir?" → Mencionar explícitamente en texto

---

### 48. Index (Blog Principal)
**Archivo:** `index.html`  
**Categoría:** Página principal del blog  
**Estado:**
| FAQ Schema | FAQ Visible | FAQ Match | Tabla Semántica | Prioridad |
|---|---|---|---|---|
| ✅ | ✅ (en schema) | ✅ (blog-level FAQ) | ❌ | 🟢 Baja |

**Nota:** Es la página principal del listado de artículos, no un artículo en sí. El FAQPage es apropiado para el blog en general.

---

## Resumen de Prioridades

### 🔴 Prioridad Alta (acción inmediata recomendada)
| # | Archivo | Problema Principal |
|---|---|---|
| 1 | `precio-certificado-energetico-2026.html` | Sin FAQ visible + schema genérico |
| 2 | `certificado-energetico-alquiler.html` | Sin FAQ visible + schema genérico |
| 3 | `caducidad-certificado-energetico.html` | FAQ schema desalineado (habla de ayudas, no de caducidad) |
| 4 | `mejorar-eficiencia-energetica-vivienda.html` | Sin FAQ visible + schema genérico |
| 5 | `plantilla-informe-energetico.html` | **Sin FAQPage schema** + sin FAQ visible |
| 6 | `precios-certificado-energetico-provincias-2026.html` | Sin FAQ visible + tablas no semánticas |

### 🟡 Prioridad Media
| # | Archivo | Problema Principal |
|---|---|---|
| 7 | `que-es-certificado-energetico.html` | FAQ schema genérico |
| 8 | `certificado-energetico-obra-nueva.html` | FAQ schema genérico |
| 9 | `certificado-energetico-online.html` | FAQ schema parcialmente genérico |
| 10 | `certificado-energetico-vender-piso.html` | FAQ schema parcialmente genérico |
| 11 | `certificado-energetico-cedula-habitabilidad.html` | FAQ schema genérico |
| 12 | `certificado-energetico-sin-visita.html` | FAQ schema genérico |
| 13 | `aerotermia-certificado-energetico.html` | Sin FAQ visible |
| 14 | `placas-solares-certificado-energetico.html` | Sin FAQ visible |
| 15 | `normativa-certificacion-energetica-espana.html` | Sin FAQ visible |
| 16 | `normativa-cee-2026.html` | Sin FAQ visible |
| 17 | `rd-659-2025-fp-superior-certificado-energetico.html` | Sin FAQ visible |
| 18 | `certificado-energetico-garajes-locales.html` | Sin FAQ visible |
| 19 | `certificado-energetico-locales-comerciales.html` | Sin FAQ visible |
| 20 | `certificado-energetico-venta.html` | Sin FAQ visible |
| 21 | `errores-comunes-cee.html` | Sin FAQ visible |
| 22 | `como-darse-de-alta-tecnico-certificador.html` | Sin FAQ visible |
| 23 | `etiqueta-energetica-edificios.html` | Sin FAQ visible |
| 24 | `hulc-cype-vs-ce3x.html` | Sin FAQ visible |
| 25 | `guia-subvenciones-rehabilitacion-energetica-2026.html` | Sin FAQ visible |
| 26 | `rehabilitacion-energetica-edificios.html` | Sin FAQ visible |
| 27 | `registro-cee-comunidades-autonomas.html` | Sin FAQ visible |
| 28 | `registro-centralizado-tecnicos-certificadores.html` | Sin FAQ visible |
| 29 | `vpo-certificado-energetico.html` | Sin FAQ visible |
| 30 | `vivienda-estandar-espana-medidas-precio-cee.html` | Sin FAQ visible |

### 🟢 Prioridad Baja (buen estado general)
| # | Archivo | Estado |
|---|---|---|
| 31 | `sanciones-certificado-energetico-2026.html` | Buen estado ✅ |
| 32 | `certificado-energetico-obligatorio-2026.html` | Buen estado ✅ |
| 33 | `certificado-energetico-alquiler-vacacional.html` | Buen estado ✅ |
| 34 | `garaje-trasero-necesita-certificado-energetico.html` | Buen estado ✅ |
| 35 | `cee-hipoteca-banco.html` | Buen estado ✅ |
| 36 | `certificado-energetico-segunda-vivienda.html` | Buen estado ✅ |
| 37 | `reforma-certificado-energetico-2026-cambios.html` | Buen estado ✅ |
| 38 | `directiva-ue-2024-1275-rehabilitacion-obligatoria.html` | Buen estado ✅ |
| 39 | `guia-ce3x-tecnicos.html` | Buen estado ✅ |
| 40 | `guia-ce3x-avanzada.html` | Buen estado ✅ |
| 41 | `ayudas-21400-euros-rehabilitacion-2026.html` | Buen estado ✅ |
| 42 | `subvenciones-rehabilitacion-20mil-plazo-30-junio.html` | Buen estado ✅ |
| 43 | `ultimos-dias-ayudas-20000-euros-rehabilitacion-2026.html` | Buen estado ✅ |
| 44 | `plan-social-clima-9099-millones-ayudas.html` | Buen estado ✅ |
| 45 | `se-acaba-dinero-europeo-guia-comunidades-vecinos.html` | Buen estado ✅ |
| 46 | `obligacion-reformar-viviendas-guia-2026-2030.html` | Buen estado ✅ |
| 47 | `index.html` | Blog principal, FAQ general ✅ |

---

## Problemas Transversales Detectados

### 1. FAQPage Schema Genérico Duplicado en Múltiples Artículos
Más del 60% de los artículos usan **exactamente las mismas 6 preguntas genéricas** en su FAQPage schema:
- ¿Qué es el certificado energético (CEE)?
- ¿Es obligatorio el certificado energético?
- ¿Cuánto cuesta un certificado energético?
- ¿Quién puede emitir el certificado energético?
- ¿Cuánto tarda el proceso completo?
- ¿Cómo puedo mejorar la letra de mi certificado?

⚠️ **Google penaliza la repetición de contenido structured data idéntico.** Cada artículo debe tener preguntas específicas de su tema.

### 2. Artículos Sin FAQ Visible en la Página
Aproximadamente 24 artículos tienen FAQPage schema en JSON-LD **pero no muestran las preguntas visibles en la página**. Google puede considerar esto como una mala práctica (datos estructurados sin contenido visible correspondiente).

### 3. Tablas Sin Marcado Semántico
Solo 13 de 48 artículos (27%) usan `<thead>`, `<th>` y `<tbody>` en sus tablas. El resto usa `<div>` con CSS para simular tablas, o tablas HTML sin semántica de encabezados.

### 4. Duplicación de FAQPage Schema
`rd-659-2025-que-cambia-tu-certificado-energetico.html` tiene dos bloques FAQPage duplicados.

### 5. FAQPage Desalineado con el Contenido
`caducidad-certificado-energetico.html` tiene preguntas sobre "ayudas y subvenciones" en su FAQ schema, pero el artículo trata sobre la caducidad del CEE.

---

## Recomendaciones Clave para Featured Snippets

### Qué snippets capturar
Los artículos con mejor potencial de featured snippet son:

| Tipo de Snippet | Artículos Candidatos | Formato |
|---|---|---|
| **Párrafo** ("¿Qué es...?") | que-es-certificado-energetico, obligatorio-2026 | Párrafo directo < 50 palabras |
| **Lista** ("Cómo... pasos") | mejorar-eficiencia, como-darse-de-alta, certificado-online | `<ol>` o `<ul>` con 3-7 items |
| **Tabla** ("Precios por...") | precio-certificado-energetico-2026, precios-provincias | Tabla con `<thead>` semántico |
| **Lista numerada** ("Pasos para...") | certificado-energetico-alquiler, certificado-online | `<ol>` numerado |

### Estructura de párrafo óptima para snippet
```
[Pregunta del usuario en h2]
[Respuesta directa en el primer párrafo siguiente: 40-60 palabras, 
incluyendo la palabra clave y datos concretos]
[Párrafo de desarrollo con detalles y contexto]
```

### Checklist de implementación por artículo
1. ✅ Añadir sección FAQ visible con `<h2>Preguntas frecuentes</h2>` o `<h2>FAQ</h2>`
2. ✅ FAQPage schema con preguntas ESPECÍFICAS del artículo (no copia genérica)
3. ✅ Cada pregunta del schema debe tener su equivalente visible en la página
4. ✅ Convertir tablas existentes a marcado semántico `<thead><th><tbody>`
5. ✅ Añadir respuestas directas (40-60 palabras) debajo de los h2 que respondan "Qué", "Cómo", "Cuánto", "Dónde"
6. ✅ Para listas: asegurar que el contexto inmediato (h2/h3 anterior) contenga la pregunta completa

---

## Notas Técnicas

- **Archivos ignorados**: `test-write2.html` (página de prueba, 30 líneas), `certificado-energetico-obligatorio-2026-v2.html` (redirección a garajes-locales)
- **Schema adicional presente**: Todos los artículos tienen BlogPosting, Article, y BreadcrumbList además de FAQPage
- **Plantilla de FAQ visible recomendada**: Incluir al final del `<div class="article-body">` antes de los related posts
- **Ubicación de FAQPage schema**: Dentro del `<head>` dentro de `<script type="application/ld+json">`
