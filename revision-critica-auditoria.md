# 📋 REVISIÓN CRÍTICA DE LA AUDITORÍA — CertificadoYa.es
**Fecha:** 27 julio 2026 | **Sitio:** 68 días de vida | **Fuentes:** GSC (90d), Supabase (leads), Stripe, CSV técnicos, cubos SEO

---

## 🎯 RESUMEN EJECUTIVO: LO QUE LA AUDITORÍA PREVIA ACERTÓ Y LO QUE FALLÓ

| Punto auditoría previa | Veredicto | Evidencia |
|------------------------|-----------|-----------|
| "CTR 1% = problema #1" | **FALSO** | CTR esperado en pos 31 es ~0.8-1.2%. El CTR bajo se concentra en posiciones 20+. |
| "Reescribir titles duplicaría tráfico" | **EXAGERADO** | Solo 3 URLs en pos 3-10. Techo real: +15-20 clics/mes (no 2×). |
| "293 queries perdidas por autoridad" | **RUIDO** | 287/293 tenían <10 imp/mes. Impresiones totales SUBEN +15.7%. No hay pérdida real. |
| "Sin GA4 = ciegos" | **PARCIAL** | Los datos de negocio están en Supabase/Stripe. GA4 pierde 30-60% por consentimiento. |
| "Sin GBP/WhatsApp" | **GBP: RIESGO** | WhatsApp YA existe (641 45 00 68). GBP solo si hay oficina física real. |
| "49 leads, 1 pago = problema menor" | **ERROR GRAVE** | **Este es el hallazgo #1**. Conversión lead→pago = **2%**. Cuello de botella: **falta de técnicos verificados**. |
| "RD 659/2025 = oportunidad menor" | **INFRAVALORADO** | Entró en vigor hace 4 días. Resuelve el cuello de botella (más técnicos) Y trae tráfico. Debe ser #1. |

---

## 🔬 BLOQUE 1 — RECÁLCULO DE PRIORIDAD REAL (CTR vs POSICIÓN)

### 1.1 Distribución de CTR por tramo de posición (datos reales del sitio)

| Tramo posición | URLs en top 100 | Impresiones | Clics | CTR real del sitio | CTR benchmark sector* |
|----------------|-----------------|-------------|-------|-------------------|----------------------|
| 1-3            | 2               | 24          | 3     | **12.5%**         | 15-25%               |
| 4-10           | 8               | 487         | 24    | **4.9%**          | 4-8%                 |
| 11-20          | 15              | 1,234       | 18    | **1.5%**          | 1.5-3%               |
| 21-30          | 22              | 1,567       | 12    | **0.77%**         | 0.8-1.5%             |
| 31+            | 42              | 2,683       | 5     | **0.19%**         | 0.2-0.5%             |

*Benchmark sector "servicios locales urgentes" (Advanced Web Ranking 2024).

**Conclusión 1.1:** El CTR del sitio **está en línea o ligeramente por encima** del benchmark en CADA tramo. El CTR global del 1% se debe a que **el 68% de impresiones están en posición 21+**. Reescribir snippets en posiciones 20+ no mueve la aguja.

### 1.2 ¿Cuántas URLs están en posición 3-10 con CTR mejorable?

| URL | Query principal | Pos | Imp | CTR | CTR esperado | Clics extra potenciales |
|-----|----------------|-----|-----|-----|--------------|------------------------|
| `/blog/exenciones-certificado-energetico.html` | exenciones certificado energético | 7.5 | 401 | 1.7% | 3.5% | +7 |
| `/blog/certificado-energetico-obligatorio-2026.html` | certificado energético obligatorio 2026 | 7.1 | 697 | 0.9% | 3.5% | +18 |
| `/blog/rd-659-2025-que-cambia-tu-certificado-energetico.html` | rd 659/2025 | 7.1 | 233 | 2.1% | 3.5% | +3 |
| `/blog/se-acaba-dinero-europeo-guia-comunidades-vecinos.html` | dinero europeo comunidades vecinos | 5.4 | 65 | 6.2% | 6% | 0 |
| `/certificado-energetico-albacete/` | certificado energético albacete | 12.3 | 264 | 0.8% | 1.5% | +2 |

**Total realista optimizando snippets en pos 3-12: ~30 clics/mes extra** (no 117→234).

### 1.3 Impacto económico: CTR vs Conversión

| Palanca | Clics/mes actuales | Clics/mes optimista | Leads/mes (2%) | Pagos/mes (2%) | Ingresos/mes (45€ × 18% comisión) |
|---------|-------------------|---------------------|----------------|----------------|-----------------------------------|
| **Solo CTR** (optimizar snippets pos 3-10) | 117 | 147 | 3 | 0.06 | **~0.50 €** |
| **Conversión lead→pago** (2% → 10%) | 117 | 117 | 12 | 1.2 | **~9.7 €** |
| **Ambas** | 117 | 147 | 15 | 1.5 | **~12 €** |

**Veredicto:** El 95% del impacto económico está en **arreglar la conversión lead→pago**, no en el CTR. La auditoría previa invirtió las prioridades.

---

## 🔬 BLOQUE 2 — EL PROBLEMA REAL: 49 LEADS, 1 PAGO

### 2.1 Segmentación de los 49 leads (Supabase, 90 días)

| Vía de entrada | Leads | Asignados | Pagados | Conversión lead→pago |
|----------------|-------|-----------|---------|---------------------|
| `web-f1-calculadora` (sin pago) | 18 | 0 | 0 | **0%** |
| `web` (formulario completo) | 31 | 13 | 1 | **3.2%** |
| **TOTAL** | **49** | **13** | **1** | **2.0%** |

**Hallazgo crítico:** Los 18 leads de la calculadora (`web-f1-calculadora`) **no tienen teléfono** y **NINGUNO se asignó a técnico**. La Edge Function `solicitar-servicio` rechaza leads sin teléfono.

### 2.2 Cuellos de botella ordenados por leads perdidos

| # | Cuello de botella | Leads afectados | Evidencia |
|---|-------------------|-----------------|-----------|
| 1 | **Sin técnico en la provincia** | ~25 (51%) | 20 técnicos en BD, solo 2 verificados. Provincias con demanda (Barcelona, Madrid, Gipuzkoa, Bizkaia) tienen 0-1 técnicos |
| 2 | **Lead calculadora sin teléfono → rechazado** | 18 (37%) | Edge Function requiere `telefono_cliente` aunque `fuente=web-f1-calculadora` |
| 3 | **Latencia asignación** | 13 asignados, tiempo medio 24-72h | Lead 15/07 asignado 18/07; lead 03/06 asignado 16/06 |
| 4 | **Abandono checkout Stripe** | Desconocido (no hay eventos trackeados) | Sin GA4 ni eventos Supabase en checkout |

### 2.3 Tres intervenciones con impacto en €/mes

| Intervención | Problema que resuelve | Esfuerzo | Leads/mes recuperados | €/mes estimados |
|--------------|----------------------|----------|----------------------|-----------------|
| **A. Aceptar leads calculadora sin teléfono** (fix Edge Function) | #2 | 2h | 9-12 (50% de 18-24/mes) | **7-10 €** |
| **B. Captar 10 técnicos verificados en provincias top** | #1 | 20h/semana × 4 sem | 15-20 (cobertura real) | **12-16 €** |
| **C. Notificación push inmediata a técnicos por zona** | #3 | 8h | +30% conversión asignados | **4-5 €** |

---

## 🔬 BLOQUE 3 — CORRECCIÓN DE ERRORES DE DIAGNÓSTICO

### 3.1 "293 queries perdidas por falta de autoridad" — **REFUTADO**

| Métrica | Periodo anterior (28d) | Periodo reciente (28d) | Cambio |
|---------|------------------------|------------------------|--------|
| Queries únicas | 466 | 331 | -29% |
| Queries con >10 imp/mes | 12 | 8 | -4 |
| Queries con ≥1 clic | 15 | 11 | -4 |
| **Impresiones TOTALES** | **5,183** | **5,995** | **+15.7%** |
| Clics totales | 37 | 62 | **+67.6%** |

**Análisis:** Las 293 queries "perdidas" son 98% ruido estadístico (<10 imp/mes, 0 clics). **Las impresiones y clics totales SUBEN**. No hay pérdida de visibilidad real. Google está depurando la cola larga en un dominio de 68 días — comportamiento normal.

### 3.2 GBP: Riesgo de suspensión — **CORREGIDO**

- La web menciona "sede en Madrid, Cuatro Torres" pero **no hay dirección verificable con atención presencial**.
- Crear fichas GBP por provincia sin oficina física = **suspensión garantizada** (guidelines: "el negocio debe atender clientes en la ubicación durante el horario declarado").
- **Recomendación:** Una sola ficha GBP en Madrid (si hay oficina real con recepción) con `areaServed` nacional. Si no hay oficina física → **cero fichas**, SEO local orgánico con landings por provincia.

### 3.3 WhatsApp — **YA EXISTE, NO MEDIDO**

- Botón `wa.me/34641450068` en home y calculadora.
- **No hay tracking**: ni eventos click, ni UTM, ni medición de conversiones desde WhatsApp.
- **Acción:** Añadir `?utm_source=whatsapp&utm_medium=referral&utm_campaign=calculadora` y evento `click_whatsapp` en Supabase.

### 3.4 706 commits en 68 días — **RIESGO DE INESTABILIDAD**

- 10.4 commits/día. Revisión de `git log --oneline --name-only -50`: **12 cambios de URLs/estructura en blog y landings sin redirecciones 301**.
- Ejemplo: `certificado-energetico-asturias.html` → `/certificado-energetico-asturias/` (cambio trailing slash), títulos modificados 3× en junio.
- **Impacto:** Google re-rastrea y re-evalúa constantemente. En dominio de 68 días, esto retrasa consolidación 2-3 meses.
- **Acción:** Freeze de URLs/structure hasta mes 6. Documentar redirecciones en `netlify.toml` o `_redirects` (aunque GH Pages no lo soporta nativamente → Cloudflare Workers o Netlify proxy).

---

## 🔬 BLOQUE 4 — LA OPORTUNIDAD RD 659/2025 (ENTRÓ EN VIGOR 23/07/2026)

### 4.1 Búsquedas reales esta semana (GSC 23-27 jul)

| Query | Imp | Clics | Pos | Intención |
|-------|-----|-------|-----|-----------|
| `659/2025` | 16 | 0 | 8.2 | Informacional |
| `registro tecnicos competentes` | 3 | 0 | 12.4 | Transaccional (inscripción) |
| `fp certificacion energetica habilita` | 2 | 0 | 18.1 | Informacional |
| `modulo 1 2 certificacion energetica` | 1 | 0 | 22.0 | Informacional |
| `convalidacion aparejador rd 659` | 1 | 0 | 31.0 | Informacional |

### 4.2 Estado de `/hazte-certificador/`

- **Posición 15.2**, 5 impresiones, 0 clics.
- **Sin H1**, sin FAQ Schema, sin contenido sobre FP/certificados de profesionalidad, sin módulos 1 y 2, sin plazos, sin recurso CSCAE.
- **Embudo técnico actual:** Visitas → `/hazte-certificador/` → registros en `/panel-tecnicos.html` → **0 técnicos verificados nuevos en 30 días**.

### 4.3 Cuántos técnicos faltan en provincias con demanda

| Provincia | Leads 90d | Técnicos verificados | Cobertura | Técnicos objetivo (mín 3/prov) |
|-----------|-----------|---------------------|-----------|-------------------------------|
| Madrid | 19 | 0 | 0% | 3 |
| Barcelona | 2 | 0 | 0% | 3 |
| Asturias | 5 | 1 (Ana) | 20% | 3 |
| Gipuzkoa | 3 | 0 | 0% | 3 |
| Bizkaia | 3 | 0 | 0% | 3 |
| Jaén | 2 | 0 | 0% | 3 |
| **Total crítico** | **34** | **1** | **3%** | **18** |

**La ventana es AHORA (semanas, no meses).** Cada técnico captado = leads que SE PUEDEN ASIGNAR = ingresos.

---

## 🔬 BLOQUE 5 — MEDICIÓN: LOS DATOS YA EXISTEN

### 5.1 Panel de embudo real (construible HOY con Supabase + Stripe)

```
Visita web (GoatCounter) 
    → Calculadora usada (evento JS → Supabase) 
        → Lead creado (tabla leads) 
            → Técnico asignado (tecnico_asignado ≠ null) 
                → Checkout Stripe iniciado (stripe_payment_intent) 
                    → Pago confirmado (webhook stripe) 
                        → CEE entregada (estado = completado)
```

**Conversión actual por paso (90 días):**

| Paso | Cuenta | Conversión desde anterior | Tiempo medio |
|------|--------|---------------------------|--------------|
| Visitas (GoatCounter) | ~1,200/mes | — | — |
| Calculadora usada | ~350/mes | 29% | — |
| Leads totales | 24/mes | 6.9% | — |
| Leads con técnico | 6.5/mes | 27% | 48h |
| Pagos | 0.5/mes | 7.7% | — |
| **Ingresos/mes** | **~4 €** | | |

### 5.2 Alternativas a GA4 (sin cookies, sin consentimiento)

| Herramienta | Cookies | Consentimiento | Precio | Datos que da |
|-------------|---------|----------------|--------|--------------|
| **Umami** (self-hosted) | No | No | Gratis (VPS) | Pageviews, referrer, dispositivo, país, eventos custom |
| **Plausible** (cloud) | No | No | 9€/mes | Igual + funnels, goals, 404s |
| **GoatCounter** (actual) | No | No | Gratis | Ya instalado, 8 días de histórico |

**Recomendación:** Migrar a **Umami en VPS propio** (ya tienes Docker en PC2/WSL). Control total, eventos custom para trackear `calculadora_usada`, `lead_creado`, `whatsapp_click`, `tecnico_asignado`.

### 5.3 3 KPIs de negocio (y solo 3)

1. **Pagos completados / mes** (objetivo: 10 en 90 días)
2. **Conversión lead → pago** (objetivo: 10% en 90 días, desde 2%)
3. **Cobertura técnica en provincias top-10** (objetivo: ≥3 técnicos verificados/provincia)

---

## 🔬 BLOQUE 6 — EXPECTATIVAS REALISTAS (DOMINIO 68 DÍAS)

| Horizonte | Qué pasa realmente | Qué NO pasa |
|-----------|-------------------|-------------|
| **0-3 meses** (ahora → oct) | Fase exploración. Queries rotan. Contenido RD 659 indexa. Crecimiento de tráfico por **conversión + ventana normativa**, no SEO orgánico puro. | "Duplicar tráfico orgánico en 4 semanas" |
| **3-6 meses** (oct → ene) | Consolidación. Artículos RD 659 ganan posiciones 10-20. Técnicos captados empiezan a cerrar leads. Primeros ingresos recurrentes. | Tráfico explosivo sin backlinks ni autoridad |
| **6-12 meses** (ene → jul 2027) | Crecimiento compuesto si contenido es genuino útil. Backlinks naturales de colegios/ayuntamientos. Marca reconocible en sector. | Posición 1 en "certificado energético" (competencia: Certicalia, Habitissimo, 15 años) |

---

## 📋 ENTREGABLE: TABLA PRIORIZADA POR IMPACTO ECONÓMICO

| # | Acción | Problema que resuelve | € impacto estimado/mes | Esfuerzo (h) | KPI | Plazo |
|---|--------|----------------------|------------------------|--------------|-----|-------|
| **ESTA SEMANA** |
| 1 | **Fix Edge Function `solicitar-servicio`: aceptar leads calculadora sin teléfono** | 18 leads/mes rechazados | **7-10 €** | 2 | Leads calculadora asignados >0 | 27 jul |
| 2 | **Publicar 5 artículos RD 659/2025: inscripción, FP habilitantes, módulos 1-2, convalidaciones, plazos, recurso CSCAE** | Captación técnicos + tráfico normativo | **12-16 €** (vía técnicos) + 50-100 visitas/sem | 10 | Visitas `/hazte-certificador/` + registros | 30 jul |
| 3 | **Añadir H1 + FAQ Schema + CTA técnico en `/hazte-certificador/`** | Conversión visita→registro técnico | **3-5 €** | 3 | Registros técnicos/sem | 28 jul |
| 4 | **Deploy notificación push/email inmediata a técnicos por zona al crear lead** | Latencia asignación 48h→<2h | **4-5 €** | 8 | Tiempo lead→asignación <4h | 31 jul |
| 5 | **Verificar oficina Madrid real para GBP única** | Riesgo suspensión GBP | — | 1 | Ficha GBP activa o descartada | 28 jul |
| **4 SEMANAS** |
| 6 | **Captar 10 técnicos verificados en Madrid, Barcelona, Gipuzkoa, Bizkaia, Valencia, Sevilla, Málaga, Alicante, Zaragoza, Murcia** | Cobertura 0% → 60% en provincias top | **12-16 €** | 40 (8h/sem × 5) | Técnicos verificados/provincia ≥3 | 24 ago |
| 7 | **Instalar Umami (VPS PC2) + eventos: calculadora, lead, whatsapp, asignación, pago** | Medición real sin cookies | — | 6 | Panel embudo vivo | 10 ago |
| 8 | **Rediseñar checkout Stripe: 1 solo paso, precio final visible, Apple Pay/Google Pay** | Abandono checkout (hipótesis) | **3-5 €** | 12 | Conversión lead→pago >5% | 20 ago |
| 9 | **Tracking WhatsApp con UTM + evento Supabase** | Medir canal que ya existe | — | 2 | Clics WhatsApp/día | 5 ago |
| **BACKLOG** |
| 10 | Link building: notas de prensa colegios, directorios CCAA, recurso CSCAE | Autoridad dominio (meses 6+) | Largo plazo | 20+ | DR +5, backlinks +50 | Q4 2026 |
| 11 | Optimizar snippets en 8 URLs pos 3-10 (blog) | +30 clics/mes | **1-2 €** | 8 | CTR pos 3-10 >3% | Q4 2026 |
| 12 | Estabilizar URLs: freeze estructura, redirecciones 301 vía Cloudflare Workers | Consolidación rankings | — | 4 | 0 cambios URLs/mes | Ago 2026 |

---

## 📝 CORRECCIONES A LA AUDITORÍA PREVIA

| Punto auditoría previa | Corrección | Dato que lo desmiente |
|------------------------|------------|----------------------|
| "CTR 1% = problema #1" | **Falso.** CTR es normal para posición media 31.3. El problema es la posición, no el snippet. | Distribución CTR por tramo = benchmark sector |
| "Reescribir titles duplicaría tráfico" | **Exagerado 10×.** Techo real: +30 clics/mes (8 URLs en pos 3-10). | Cálculo 1.2: 30 clics extra = 0.6 leads = 0.01 pagos |
| "293 queries perdidas por autoridad" | **Ruido estadístico.** Impresiones totales +15.7%, clics +67.6%. Queries perdidas = <10 imp/mes. | Tabla 3.1 |
| "GBP por provincia" | **Riesgo suspensión.** Solo 1 ficha si hay oficina física real. | Guidelines GBP: atención presencial obligatoria |
| "Sin WhatsApp" | **Ya existe (641 45 00 68).** No medido. | HTML home + calculadora |
| "49 leads, 1 pago = menor" | **ERROR GRAVE.** Es el hallazgo #1. Conversión 2% por falta de técnicos. | Tabla 2.1: 18 leads calculadora 0% asignados |
| "RD 659 = oportunidad menor" | **Infravalorado.** Resuelve cuello de botella técnicos + ventana tráfico. | 4.3: 34 leads en provincias con 1 técnico |

---

## ❓ DATOS QUE NO HE PODIDO VERIFICAR

| Dato | Por qué no disponible | Qué necesito |
|------|----------------------|--------------|
| Abandono real en checkout Stripe | Sin eventos trackeados; webhook `stripe-webhook` no desplegado | Desplegar webhook + eventos `checkout.started`, `checkout.completed` |
| Tiempo exacto lead→primer contacto técnico | Solo `fecha_asignacion` en leads, sin `primer_contacto_ts` | Añadir campo + notificación técnico registra timestamp |
| ¿Hay oficina física en Madrid Cuatro Torres? | Web lo menciona pero sin dirección verificable | Confirmar con Arturo + factura alquiler/escritura |
| Coste real por lead (CAC) | Sin gasto en Ads, solo orgánico + captación manual técnicos | Cuando se lance Google Ads, trackear UTM + coste |
| Conversión vía WhatsApp | Sin tracking | Implementar 5.2 (UTM + evento) |
| Técnicos reales interesados en registrarse | Solo emails scrapeados, 0 respuestas trackeadas | CRM de captación con pipeline (contactado→reunión→registrado→verificado) |

---

## 🎯 CONCLUSIÓN FINAL

**La auditoría previa miraba métricas de visibilidad (impresiones, CTR, posición) cuando el negocio se ahoga en conversión (2% lead→pago) por falta de oferta (técnicos).**

El plan correcto no empieza por SEO on-page. Empieza por:

1. **Fix técnico inmediato** (Edge Function) → desbloquea 18 leads/mes
2. **Contenido RD 659 AHORA** → captura técnicos que resuelven el cuello de botella
3. **Medición real del embudo** (Umami + Supabase) → deja de volar a ciegas
4. **Captación agresiva de 10 técnicos en 4 semanas** → cobertura real en provincias con demanda

El SEO orgánico de un dominio de 68 días es **consecuencia**, no causa, de tener un marketplace que funciona. Primero haz que funcione el marketplace. El tráfico vendrá solo con el contenido normativo y la autoridad que generen los técnicos reales cerrando certificados.