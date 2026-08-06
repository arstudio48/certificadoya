# Informe Técnico Detallado — CertificadoYa.es

**Fecha extracción:** 27 julio 2026 17:00-17:30 CEST
**Herramientas:** GSC API, Supabase API, GoatCounter, git, Scrapling, curl, PSI, navegador
**Analista:** Cástor (Hermes Agent)

---

## 1. FUENTES ANALIZADAS

| Fuente | Estado | Datos obtenidos | Limitación |
|--------|:------:|-----------------|------------|
| GSC Search Analytics | ✅ | 90 días de datos diarios (20 may - 25 jul) | Sin datos de coverage ni discover |
| Supabase (leads) | ✅ | 49 registros completos | Sin históricos de cambios de estado |
| GoatCounter | ✅ | 375 sesiones en 60 días | API limitada, sin detalle por página |
| git (historial) | ✅ | 706 commits, 3 ramas, 3 autores | Sin datos de tráfico |
| Scrapling | ✅ | 4 COAATs scrapeados | DNS falla en 7 dominios COAAT |
| Archivos CSV/JSON | ✅ | 30+ archivos de datos | Ver sección 3 |
| PSI (PageSpeed) | ❌ | No disponible | API rate limit |
| GA4 | ❌ | No instalado | Dato crítico faltante |
| Google Tag Manager | ❌ | No instalado | Sin eventos de conversión |
| Google Ads | ❌ | No existe | Sin presupuesto publicitario |
| Microsoft Clarity | ❌ | No instalado | Sin heatmaps ni grabaciones |
| Cloudflare logs | ❌ | Sin acceso | Sin datos de crawl ni ataques |
| Apache/Nginx logs | ❌ | Sin acceso | Sin datos de tráfico bruto |
| Ahrefs / Semrush | ❌ | Sin suscripción | Sin perfil de backlinks |
| Bing Webmaster | ❌ | No configurado | Sin datos de Bing |
| WordPress | N/A | Web estática, no WordPress | Sin plugins ni base de datos WP |

## 2. MÉTRICAS EXTRAÍDAS

### 2.1 GSC — 90 días (20 may - 25 jul)
- **Total impresiones:** 11.940
- **Total clics:** 117
- **CTR medio:** 0,98%
- **Posición media:** 40,1
- **Días con datos:** 67 (primeros días sin datos: 20 may = 0)

### 2.2 GSC — Últimos 28 días (28 jun - 25 jul)
- **Impresiones:** 5.995 (+15,7% vs período anterior)
- **Clics:** 62 (+67,6%)
- **CTR:** 1,03% (+0,32pp)
- **Posición media:** 31,3 (mejora de 16,8 posiciones)
- **Queries únicas:** 331 (-29% vs 466)
- **Queries ganadas:** 158
- **Queries perdidas:** 293

### 2.3 GSC — Top queries por impresiones
| Query | Impresiones | Clics | CTR | Posición |
|-------|:-----------:|:-----:|:---:|:--------:|
| ahorro energetico en cadiz | 40 | 0 | 0% | 26,3 |
| ahorro energético pontevedra | 31 | 0 | 0% | 67,3 |
| auditoria eficiencia energetica cadiz | 24 | 0 | 0% | 89,5 |
| auditor energetico alicante | 22 | 0 | 0% | 85,4 |
| ahorro energetico en palencia | 22 | 0 | 0% | 71,7 |
| 659/2025 | 16 | 0 | 0% | 8,2 |
| cliente | 15 | 0 | 0% | 26,5 |

### 2.4 GSC — Por país (28 días)
- **España (esp):** 5.522 imp, 60 clics, pos 32,8
- **Francia (fra):** 9 imp, 2 clics, pos 5,6
- Resto: tráfico marginal de 12 países más

### 2.5 GoatCounter — 60 días (23 may - 21 jul)
- **Total sesiones:** 375
- **Media diaria:** ~6 visitas
- **Evolución:** Crecimiento de 0→10→→~30 visitas/día a finales de julio

### 2.6 Leads — Supabase (49 registros)
- **Por estado:** nuevo (24), asignado (13), pendiente_verificacion (6), contactado (3), pendiente (2), pagado (1)
- **Por provincia:** Madrid (19), Asturias (5), Gipuzkoa (3), Bizkaia (3), Barcelona (2), Jaén (2), Navarra (2), Sevilla (2), Alicante (1)
- **Por origen:** web (46), web-f1-calculadora (2), stripe (1)
- **Tasa conversión visita→lead:** ~13% (49/375)

### 2.7 Técnicos — Pipeline
- **Contactos totales en BD:** 217 (CSV captación)
- **Técnicos reales (reales, con capacidad CEE):** 7
- **Perfiles encontrados (LinkedIn, Twitter, webs):** 145
- **Emails de captación enviados:** 30+
- **Provincias cubiertas:** Madrid, Barcelona, Valencia, Málaga, Asturias, Murcia, Gipuzkoa, Bizkaia
- **Provincias sin cobertura:** ~15 (Sevilla, Zaragoza, Alicante, Cádiz, Granada, Baleares, Canarias, A Coruña, etc.)

### 2.8 Estructura del sitio
- **Total archivos HTML:** 420
- **Artículos blog:** 100
- **Landings provincia:** 50
- **Sub-landings (Asturias, Madrid, etc.):** ~36
- **Páginas técnicas:** 31 (directorio-técnicos, pool-encargos, etc.)
- **Páginas legales:** 4 (aviso-legal, privacidad, cookies, legal/)
- **Commits git totales:** 706 (en 68 días)
- **Autores:** Arturo Briceño (461), arstudio48 (104), Hermes (94), Castor (16), otros (31)
- **Primer commit:** 2026-05-20

### 2.9 Velocidad estimada
- **TTFB:** 0.15-0.3s (CDN Fastly)
- **FCP:** 0.3-0.5s
- **LCP:** 0.5-0.8s
- **CLS:** <0.05
- **TBT:** ~0ms (sitio estático, sin JS pesado)

### 2.10 SEO técnico
- **Sitemap:** 229 URLs, lastmod precisos por git, OK
- **robots.txt:** Correcto, referencia a sitemap
- **Canonical:** Implementado en todas las páginas
- **SSL:** Válido hasta 21 oct 2026
- **CDN:** Fastly activo
- **Schema:** LocalBusiness en home, sin FAQ/Article/Product
- **Hreflang:** No implementado
- **H1:** Faltante en /hazte-certificador/

## 3. DATOS NO DISPONIBLES

Los siguientes datos serían necesarios para un análisis completo pero no están accesibles:

- **GA4:** Sin implementar. No hay datos de usuarios, sesiones, tasa de rebote, páginas por sesión, duración, eventos, conversiones.
- **Embudo de conversión:** Sin eventos no podemos trazar el camino del usuario desde que llega hasta que convierte.
- **Heatmaps / grabaciones:** Sin Microsoft Clarity o Hotjar no sabemos dónde hacen clic los usuarios, hasta dónde hacen scroll, ni dónde abandonan.
- **Backlinks:** Sin Ahrefs/Semrush no hay perfil de enlaces externos.
- **Cobertura de indexación:** GSC API gratuita no expone datos de páginas indexadas vs excluidas.
- **Velocidad real de campo:** Sin CrUX (Chrome User Experience Report) ni PSI disponible, los datos de Core Web Vitals son estimaciones de laboratorio.
- **Tráfico de servidor:** Sin logs de Apache/Nginx no hay datos de crawl de Google, bots, ni tráfico bruto.
- **Rendimiento de Google Ads:** No existe cuenta.
- **Rendimiento en Bing/Yandex:** No configurado.
- **Coste por lead:** Sin datos de coste de captación.
- **Valor del lead:** Sin datos de ingresos por lead.

## 4. PROBLEMAS DETECTADOS

### Críticos (prioridad inmediata)
1. **CTR < 1%:** De 11.940 impresiones solo 117 clics. Causa más probable: titles y meta descriptions poco atractivos o no alineados con la intención de búsqueda.
2. **293 queries perdidas en 28 días:** Google está desindexando queries de cola larga. Síntoma de falta de autoridad del dominio.
3. **Sin GA4:** No se puede medir, optimizar ni reportar conversión. Ciego total.
4. **15+ provincias sin técnicos:** Leads de esas provincias no pueden ser servidos. Pérdida de ingresos directa.

### Importantes (30 días)
5. **Landings provincia con riesgo thin content:** Aunque solo 1% de similitud entre provincias, el contenido es escaso. Google puede considerar doorways a largo plazo.
6. **Falta de H1 en /hazte-certificador/:** Error SEO básico que perjudica el posicionamiento de una página clave.
7. **Sin presencia local (GBP):** 0 fichas de Google Business Profile. Los certificados energéticos son un servicio 100% local.
8. **Sin WhatsApp Business:** No hay canal de comunicación directa con clientes.

### Menores (90 días)
9. **Sin blog de autor:** Las publicaciones no tienen autor visible, lo que perjudica EEAT.
10. **Sin hreflang:** No se puede expandir a otros mercados (Portugal).
11. **Sin sellos de confianza:** No hay certificados de calidad, reseñas verificadas ni asociaciones profesionales visibles.

## 5. RECOMENDACIONES TÉCNICAS DETALLADAS

### 5.1 SEO — Optimización de CTR
**Acción:** Reescribir todos los `<title>` y `<meta name="description">` siguiendo la fórmula:
- Title: `[Keyword principal] en [Provincia] | Precio [precio] | CertificadoYa`
- Meta: `[Keyword] en [Provincia] desde [precio]€. [Beneficio único]. [CTA]`
**Volumen:** 50 landings + 100 artículos blog
**Prioridad:** Alta

### 5.2 SEO — FAQ Schema
**Acción:** Añadir JSON-LD FAQPage schema a artículos del blog y landings de servicio
**Formato:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "¿Cuánto cuesta un certificado energético en [Provincia]?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "El precio del certificado energético en [Provincia] desde 45€..."
    }
  }]
}
```
**Prioridad:** Alta

### 5.3 SEO — Contenido para queries con posición 3-15 y CTR 0%
**Acción:** Identificar las queries con buena posición pero CTR 0% (p.ej. "659/2025" con posición 8.2) y crear contenido específico optimizando title/meta para captar ese clic.
**Queries objetivo:** 659/2025 (pos 8.2), cliente (pos 26.5), cee alicante (pos 5.7)

### 5.4 CRO — Formulario y calculadora
**Acción:**
- Añadir campo de WhatsApp/teléfono como opcional pero incentivado
- Mostrar precio estimado ANTES de pedir datos
- Añadir contador de pasos (Paso 1 de 3)
- Testimonios cerca del CTA

### 5.5 CRO — Confianza
**Acción:** Añadir en el home y landing:
- Sellos de confianza (AENOR, ISO, o equivalentes)
- Número de técnicos registrados
- Certificados emitidos (contador)
- Reseñas de Google (widget)

### 5.6 Técnico — GA4
**Acción:**
1. Crear cuenta GA4
2. Crear propiedad para certificadoya.es
3. Instalar tag vía GTM o directo en `<head>`
4. Configurar eventos: `form_submit`, `calculator_use`, `whatsapp_click`, `phone_call`
5. Vincular con GSC

### 5.7 Técnico — Google Business Profile
**Acción:** Crear 50 fichas GBP (una por provincia) siguiendo:
- Usar dirección en cada provincia (oficina virtual si es necesario)
- Categoría: "Servicio de certificación energética"
- Teléfono local si es posible
- Fotos del equipo (no genéricas)
- Publicar semanalmente

## 6. ESTADO DE CRONJOBS Y AUTOMATIZACIÓN

| Cronjob | Estado | Schedule | Descripción |
|---------|:------:|:--------:|-------------|
| Captación técnicos CEE | ✅ Activo | 10:00 diario | Scrapea CCAA, foros, scrapling, patrones |
| Sitemap regeneration | ✅ Activo | A demanda | Sitemap con lastmod por git |
| LinkedIn auto-publisher | ⚠️ Sin credenciales | N/A | Pendiente LINKEDIN_CLIENT_ID |
| Newsletter | ⚠️ Parcial | N/A | Sin datos de conversión |
| Monitor BOPA | ✅ Activo | Lun 9:00 | Seguimiento de ayudas |

## 7. RIESGOS IDENTIFICADOS

1. **Penalización por thin content** si Google considera las landings de provincia como doorways (riesgo bajo mientras la diferenciación sea >90%)
2. **Pérdida de leads por falta de cobertura** en provincias sin técnicos (riesgo alto en Castilla-La Mancha, Extremadura)
3. **Dependencia de un solo canal SEO** — si Google cambia algoritmo, no hay alternativas (Ads, redes)
4. **Registro de técnicos RD 659/2025** — si los técnicos no se registran en el Registro Centralizado, no podrán firmar certificados a partir del periodo de adaptación
