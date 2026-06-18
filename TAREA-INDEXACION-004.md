# TAREA: INDEXACION-004

# Proyecto: certificadoya.es · Ejecutor: Hermes Agent (DeepSeek)
# Fecha: 2026-06-12 · Prioridad: ALTA

## REGLAS (OBLIGATORIAS)

1. Orden estricto: X0 → X1 → X2 → X3 → X4. Un commit por fase, mensaje `INDEXACION-N: <título>`, push, espera 90 s, validación en vivo.
2. Cada ✅ exige la salida LITERAL del comando pegada en el informe. Un ✅ sin salida = fase NO completada.
3. PROHIBIDO inventar datos de tasas, organismos o plazos. Fuente única: `organismos-contacto.html`. Dato ausente = `[[PENDIENTE]]`.
4. PROHIBIDO tocar CSS, colores o contenido existente.
5. Trabaja por lotes de 20 páginas máximo por commit en X1 y X2.

## X0 — INVENTARIO BINARIO
0.1 Listar 99 páginas (reales: 85). 0.2 Contar enlaces. 0.3 Clasificar VIEJAS/ACTUALES.

## X1 — INTERLINKING
1.1 Mapa de cercanía (mismas CCAA primero). 1.2 Section provincias-cercanas ante-footer. 1.3 Párrafo blog tras primer H2. 1.4 VIEJAS: añadir breadcrumb. 1.5 Lotes de 20.

## X2 — BLOQUE REGISTRO CCAA
2.1 Extraer datos de organismos-contacto.html. 2.2 Section registro-ccaa. 2.3 Lotes de 20.

## X3 — LASTMOD + INDEXNOW
3.1 sitemap.xml con 2026-06-12. 3.2 python3 notificar_indexnow.py. 3.3 Commit.

## X4 — MEDICIÓN + INFORME
4.1 Similitud Jaccard. 4.2 INFORME-INDEXACION-004.md. 4.3 Telegram.
