# INFORME-LIMPIEZA-002: Parche LIMPIEZA-001

**Fecha:** 2026-06-12
**Ejecutor:** Hermes Agent (DeepSeek)
**Proyecto:** TAREA-LIMPIEZA-CRITICA-WEB-002

---

## P1 — SACAR DEL SITEMAP LAS 5 URLs UTILITARIAS

### Acciones realizadas
1. Eliminados bloques `<url>` de 5 páginas del sitemap.xml:
   - aceptar-encargo.html
   - gracias.html
   - pago-exitoso.html
   - success.html
   - pool-encargos.html
2. Verificación local de noindex en las 5 páginas: todas OK (ninguna necesitó añadido)

### Validaciones (en vivo)

**V1:** URLs eliminadas del sitemap → 0 coincidencias
```
$ curl -s https://www.certificadoya.es/sitemap.xml | grep -c -e "aceptar-encargo" -e "gracias.html" -e "pago-exitoso" -e "success.html" -e "pool-encargos"
0
```

**V2:** noindex presente en cada página (1 = presente):
```
https://www.certificadoya.es/aceptar-encargo.html: 1
https://www.certificadoya.es/gracias.html: 1
https://www.certificadoya.es/pago-exitoso.html: 1
https://www.certificadoya.es/success.html: 1
https://www.certificadoya.es/pool-encargos.html: 1
```

**Resultado P1:** ✅ COMPLETADO

---

## P2 — CERRAR LA DEDUPLICACIÓN DEL BLOG (v2)

### Acciones realizadas
1. `git mv blog/certificado-energetico-obligatorio-2026-v2.html blog/certificado-energetico-garajes-locales.html`
2. Creado stub de redirección en v2 (noindex + refresh + canonical)
3. Actualizado canonical y og:url en garajes-locales.html
4. Actualizados enlaces internos en:
   - blog/certificado-energetico-obligatorio-2026.html (enlace a artículo)
   - blog/certificado-energetico-garajes-locales.html (JSON-LD + breadcrumb)
5. Sitemap: eliminada URL antigua, añadida nueva con `<lastmod>2026-06-12</lastmod>`

### Validaciones (en vivo)

**V1:** garajes-locales devuelve 200
```
$ curl -s -o /dev/null -w "%{http_code}" https://www.certificadoya.es/blog/certificado-energetico-garajes-locales.html
200
```

**V2:** v2 tiene redirect + noindex (2 coincidencias)
```
$ curl -s https://www.certificadoya.es/blog/certificado-energetico-obligatorio-2026-v2.html | grep -c -e 'http-equiv="refresh"' -e 'noindex'
2
```

**V3:** sitemap sin obligatorio-2026-v2
```
$ curl -s https://www.certificadoya.es/sitemap.xml | grep -c "obligatorio-2026-v2"
0
```

**V4:** sitemap con garajes-locales
```
$ curl -s https://www.certificadoya.es/sitemap.xml | grep -c "garajes-locales"
1
```

**Resultado P2:** ✅ COMPLETADO

---

## P3 — TITLE Y DESCRIPTION DE LA PÁGINA MADRID

### Acciones realizadas
- `<title>` actualizado a: "Certificado Energético Madrid desde 45 € — CEE oficial en 48-72h"
- `<meta name="description">` actualizada a descripción unificada sin "Madrid Centro"
- `<meta property="og:title">` actualizado al mismo título
- `<meta name="twitter:title">` actualizado al mismo título
- Eliminadas todas las apariciones de "Madrid Centro" en title/description

### Validaciones (en vivo)

**V1:** title exacto
```
$ curl -s https://www.certificadoya.es/certificado-energetico-madrid/ | grep -o '<title>[^<]*'
<title>Certificado Energético Madrid desde 45 € — CEE oficial en 48-72h
```

**V2:** sin "Madrid Centro" en meta
```
$ curl -s https://www.certificadoya.es/certificado-energetico-madrid/ | grep -c 'content="[^"]*Madrid Centro'
0
```

**Resultado P3:** ✅ COMPLETADO

---

## P4 — RECUENTO FINAL

### Recuento sitemap
```
$ curl -s https://www.certificadoya.es/sitemap.xml | grep -c "<loc>"
138
```

Justificación:
- 143 (base LIMPIEZA-001)
- - 5 (utilitarias eliminadas P1)
- - 1 (v2 antigua eliminada P2)
- + 1 (garajes-locales nueva añadida P2)
- = 138 URLs finales

### Validación XML
```
$ python3 -c "import xml.dom.minidom; xml.dom.minidom.parse('sitemap.xml'); print('XML-OK')"
XML-OK
```

---

## RESUMEN FINAL

| Parche | Descripción | Estado |
|--------|-------------|--------|
| P1 | 5 URLs utilitarias fuera del sitemap + noindex verificado | ✅ |
| P2 | Renombrar v2 a garajes-locales + redirect + enlaces actualizados | ✅ |
| P3 | Title y description Madrid unificados (sin "Madrid Centro") | ✅ |
| P4 | Sitemap 138 URLs, XML válido, informe generado | ✅ |

**Estado global:** ✅ PARCHE-002 COMPLETADO

**Recomendación:** Reenviar sitemap.xml en Google Search Console para acelerar la reindexación.
