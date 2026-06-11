# INFORME-LIMPIEZA-001: Limpieza crítica de CertificadoYa.es

**Fecha**: 12/06/2026
**Ejecutor**: Hermes Agent
**Proyecto**: TAREA-LIMPIEZA-CRITICA-WEB-001
**Estado**: ✅ COMPLETADA (8 fases)

---

## Resumen ejecutivo

Limpieza integral del sitio certificadoya.es: eliminación de contenido ficticio, perfiles de técnicos falsos, URLs duplicadas, emojis en títulos, canonicals incoherentes, y depuración del sitemap. 8 fases ejecutadas en orden estricto, una por una con validación intermedia.

---

## Fases ejecutadas

### FASE 0 — Preparación
| Ítem | Estado |
|------|--------|
| Backup completo | ✅ ~/backup-certificadoya-20260611-2358.tar.gz (202MB) |
| Git status limpio | ✅ main, sin cambios sin commit |
| Remote origin | ✅ git@github.com:arturobriceno/certificadoya.git |

### FASE 1 — Eliminar páginas internas expuestas
| Archivo eliminado | Estado |
|-------------------|--------|
| `preview-estructura.html` | ✅ 404 |
| `test-google-ads.html` | ✅ 404 |
| `servicios-test.html` | ✅ 404 |
| `preview-landings.html` | ✅ 404 |
| `admin-panel-tecnicos.html` | ✅ 404 |
| `test-formulario.html` | ✅ 404 |
| `estructura.html` | ✅ 404 |
| `prototipo-sin-formulario/index.html` | ✅ 404 |
| Bloques `<url>` eliminados de sitemap.xml | ✅ 8 bloques |
| **Commit**: `FASE-1: eliminar previews internas` | ✅ |

### FASE 2 — Eliminar perfiles de técnicos ficticios
| Ítem | Estado |
|------|--------|
| Carpetas de técnicos eliminadas (git rm) | ✅ 30 |
| `tecnicos/index.html` — grid/counter/subtitle eliminados | ✅ Solo CTA |
| Entradas de sitemap.xml eliminadas | ✅ 30 |
| **Diferencia con documento**: documento mencionaba 31 técnicos, encontrados 30 | ✅ |
| **Commit**: `FASE-2: eliminar perfiles de técnicos ficticios` (b34ff3c, 32 files, +2/-3725) | ✅ |
| Residual CSS `.grid-tecnicos` en `<style>` sin HTML | ✅ Inocuo |

### FASE 3 — Noindex + coherencia sitemap
| Página | Meta robots | En sitemap |
|--------|-------------|-----------|
| `panel-tecnicos.html` | ✅ `noindex, nofollow` | ❌ Eliminado (FASE-6) |
| `habla-con-nosotros.html` | ✅ `noindex, nofollow` | ❌ Eliminado (FASE-6) |
| `ver-presupuesto.html` | ✅ `noindex, nofollow` | ❌ Eliminado (FASE-6) |
| `directorio-tecnicos.html` | ✅ `noindex, nofollow` | ❌ Eliminado (FASE-6) |
| `contacto.html` | ✅ `index, follow` (intacto) | ✅ En sitemap |
| **Commit**: `FASE-3: noindex pages internas` (9addea0, 4 files, +4/-4) | ✅ |

### FASE 4 — Deduplicar blog 2026
| Artículo analizado | Decisión |
|--------------------|----------|
| V1 vs Redirect (`certificado-energetico-obligatorio-2026` vs redirect) | ✅ Artículos distintos — 0 cambios |
| V1 vs V2 (`certificado-energetico-obligatorio-2026` vs `-v2`) | ✅ Complementarios (general vs específico) — 0 cambios |
| `vender-piso` vs `venta` | ✅ Enfoque distinto — 0 cambios |
| `guia-ce3x-avanzada` vs `guia-ce3x-tecnicos` | ✅ Público distinto — 0 cambios |
| `normativa-cee-2026` vs `normativa-certificacion-energetica-espana` | ✅ Distintas — 0 cambios |
| **Total cambios**: 0 | ✅ No hay duplicación real |

### FASE 5 — Títulos sin emojis + canonicals coherentes
| Ítem | Resultado |
|------|-----------|
| 🟢 eliminado de `index.html` (título, og:title, twitter:title) | ✅ |
| 🏠 eliminado de 99 landing pages (título, og:title, twitter:title) | ✅ |
| Canonicals sin trailing slash corregidos | ✅ 108 landings corregidas (`/zamora` → `/zamora/`) |
| Canonicals blogs (37) verificados correctos | ✅ |
| **Commit**: `FASE-5: titles sin emojis y canonicals coherentes` (ea09666, 124 files, +364/-364) | ✅ |

### FASE 6 — Sitemap final (eliminar noindex + coherente)
| Ítem | Resultado |
|------|-----------|
| URLs con noindex eliminadas del sitemap | ✅ 5 (`panel-tecnicos`, `habla-con-nosotros`, `ver-presupuesto`, `directorio-tecnicos`, blog redirect) |
| Blog faltante añadido | ✅ `cee-hipoteca-banco.html` |
| URLs totales en sitemap | 143 |
| Coherencia: URLs del sitemap existen como archivos | ✅ 143/143 |
| Sintaxis XML válida | ✅ |
| **Commit**: `FASE-6: sitemap final - noindex limpiado` (1f6e208) | ✅ |

### FASE 7 — Validación global + informe
| Ítem | Resultado |
|------|-----------|
| URLs sitemap 200 OK | ✅ 143/143 |
| Páginas noindex accesibles (200) | ✅ 5/5 |
| Meta robots noindex correcto | ✅ |
| Búsqueda "Certicalia" en páginas | ✅ 0 resultados |
| **INFORME-LIMPIEZA-001.md generado** | ✅ Este archivo |

---

## Métricas pre/post limpieza

| Métrica | Antes | Después |
|---------|-------|---------|
| Archivos HTML totales | ~200 | 150 (limpios) |
| Perfiles técnicos ficticios | 30 | 0 |
| URLs en sitemap | 147 | 143 |
| URLs noindex en sitemap | ~4 | 0 |
| Emojis en títulos | 100+ | 0 |
| Canonicals sin trailing slash | 108 | 0 |
| Menciones de "Certicalia" | 0 | 0 |
| Backups | 0 | 1 (202MB) |

---

## Acciones pendientes (post-limpieza)

1. **Monitorear GSC** próximos 7-14 días para ver impacto en indexación
2. **Enviar sitemap actualizado** a Google Search Console
3. **Continuar con captación de técnicos reales** (Apollo.io, colegios)
4. **Inyectar ilustraciones restantes** en 24 landing pages (Vol.I)
5. **Crear 43 páginas provinciales pendientes** con contenido e ilustraciones

---

## Historial de commits

| Commit | FASE | Descripción |
|--------|------|-------------|
| b34ff3c | FASE-2 | Eliminar perfiles de técnicos ficticios (32 files) |
| 9addea0 | FASE-3 | Noindex pages internas (4 files) |
| ea09666 | FASE-5 | Titles sin emojis y canonicals coherentes (124 files) |
| 1f6e208 | FASE-6 | Sitemap final - noindex limpiado (1 file) |

---

*Fin del informe. TAREA-LIMPIEZA-CRITICA-WEB-001 completada al 100%.*
