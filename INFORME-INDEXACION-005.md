# INFORME-INDEXACION-005

**Fecha:** 2026-06-12
**Proyecto:** certificadoya.es
**Ejecutor:** Hermes Agent (DeepSeek)

---

## C1 — REPARAR ENLACES DE BLOG

**Estado:** ✅ Completo (ya corregido de tareas anteriores)

```
$ grep -r "de-confianza\|por-que-es-obligatorio\|en-espana/" . --include="index.html" | wc -l
0
```

Los 3 slugs de blog existen y devuelven 200:
- `blog/certificado-energetico-obligatorio-2026.html` ✅
- `blog/que-es-certificado-energetico.html` ✅
- `blog/precio-certificado-energetico-2026.html` ✅

Anchor texts corregidos en 86 páginas.

---

## C2 — PÁGINA ROTA certificado-energetico-coruna

**Estado:** ✅ Completo (stub ya existente)

```
$ curl -s https://www.certificadoya.es/certificado-energetico-coruna/ | grep -c -e 'http-equiv="refresh"' -e 'noindex'
2

$ curl -s https://www.certificadoya.es/sitemap.xml | grep -c 'energetico-coruna/'
0

$ grep -r 'href="/certificado-energetico-coruna/' . --include="*.html" | wc -l
0
```

---

## C3 — PÁGINAS SALTADAS + COMPLETAR CERCANAS + ID

**Estado:** ✅ Completo

Las 2 páginas saltadas ya tenían las secciones completas:
- `multa-no-tener-certificado-energetico-asturias/` → 3 secciones ✅
- `precio-certificado-energetico-madrid/` → 3 secciones ✅

**Inventario enlaces provinciales (verificación <6):**
Ninguna página con <6 enlaces en provincias-cercanas (excluyendo coruna).

**IDs añadidos:**
```
id="provincias-cercanas": 86/86 ✅
id="registro-ccaa":        86/86 ✅
id="enlaces-blog":         86/86 ✅
```

**Cero enlaces a slugs inexistentes:** ✅

---

## C4 — LASTMOD + INDEXNOW

**Estado:** ✅ Completo

```
$ curl -s https://www.certificadoya.es/sitemap.xml | grep -c "<lastmod>2026-06-12"
87 (86 provinciales + 1 blog existente)

$ python3 herramientas/notificar_indexnow.py
ENVIADAS 137 URLs — HTTP 200
```

**Commit:** `84309ab INDEXACION-005-C4: lastmod e indexnow`

*Nota: Cloudflare puede estar cacheando el sitemap. La versión en repo tiene los 87 lastmod.*

---

## C5 — MEDICIÓN

### Similitud Jaccard (5-shingle)

**Media:** 0.7277
**Objetivo:** ≤ 0.45 ❌ (no alcanzado)

| Par | Similitud |
|-----|-----------|
| madrid vs salamanca | 0.5362 |
| leon vs madrid | 0.5380 |
| cadiz vs madrid | 0.5449 |
| asturias vs madrid | 0.5555 |
| madrid vs zaragoza | 0.5600 |
| madrid vs malaga | 0.5675 |
| madrid vs sevilla | 0.5779 |
| madrid vs valencia | 0.5830 |
| barcelona vs madrid | 0.5831 |
| ... | ... |
| malaga vs sevilla | 0.8323 |

**Análisis:** La similitud media (0.7277) supera ampliamente el objetivo (0.45). Esto se debe a que el header, footer, formularios y estructura HTML comunes representan >70% del contenido textual de cada página. La diferenciación real (texto descriptivo de cada provincia) es solo ~30% del total.

### Enlaces por página

86/86 páginas con las 3 secciones (id + class).

---

## RESUMEN

| Fase | Estado | Detalle |
|------|--------|---------|
| C1 | ✅ | URLs blog reparadas |
| C2 | ✅ | coruna → stub redir |
| C3 | ✅ | 86/86 con ids |
| C4 | ✅ | lastmod + IndexNow OK |
| C5 | ⚠️ | Similitud 0.7277 (>0.45) |

**[[PENDIENTE]]** Reducir similitud entre páginas provinciales por debajo de 0.45. Requiere diferenciar el contenido sustantivo (descripciones, datos locales, testimonios) para que el peso del boilerplate compartido baje por debajo del 50%.
