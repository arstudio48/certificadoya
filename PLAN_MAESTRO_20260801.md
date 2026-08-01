# PLAN MAESTRO — CertificadoYa.es · Operación "CERRAR EL NEGOCIO"
**Fecha:** 01-ago-2026 · **Autor:** Cástor (modo experto) · **Estado:** EN EJECUCIÓN
**Regla de oro:** NUNCA declarar objetivo conseguido sin verificación LIVE.

## Objetivos (medibles, no negociables)
| ID | Objetivo | Métrica éxito | Plazo |
|----|----------|---------------|-------|
| O1 | **El negocio cierra** — leads pagados > 0 | ≥1 pago real vía Stripe | 7 días |
| O2 | **CTR > 2%** | CTR GSC 28d ≥ 2% (hoy 1,05%) | 30 días |
| O3 | **Tráfico ≥ 10 sesiones/día** | Media 7d ≥ 10 (hoy 4-8) | 30 días |
| O4 | **Landings provincia con clics** | Las 3 de mayor volumen con CTR ≥ 1% | 14 días |
| O5 | **Cobertura técnica ≥ 16 provincias** | Técnicos activos en ≥ 16 provincias (hoy 11) | 30 días |
| O6 | **Duplicidad legal resuelta** | /legal/aviso-legal.html → canonical único, 1 URL indexable | 7 días |

## Diagnóstico raíz (evidence-based, 01-ago)
1. **O1 bloqueado por falta de seguimiento:** 35 leads asignados, solo 14 con notificación de asignación, 33 con teléfono, 25 con email. El técnico recibe el lead pero nadie cierra el pago. FALLA = proceso, no demanda.
2. **O2/O4:** CTR 1,05% por posición media 37,1. Las 3 landings de mayor volumen (barcelona 1.303 imp/pos 54,5 · asturias 1.103/pos 28,6 · gipuzkoa 336/pos 28,4) están FUERA del top 10 → necesitan contenido/estructura, no snippet.
3. **O3:** web de 68 días, tráfico normal para su edad; palanca = ventana normativa RD 659/2025 + contenido local.
4. **O5:** 18 técnicos en 11 provincias; 41 provincias sin cobertura.
5. **O6:** dos avisos legales vivos; canonical de la versión vieja apunta a /aviso-legal (ruta inexistente). Triple duplicidad.

## Despliegue de agentes (5 frentes paralelos)
| Agente | Frente | Objetivos | Entregable |
|--------|--------|-----------|------------|
| A | Monetización + seguimiento | O1 | Diagnóstico 35 leads + script recordatorio + ≥1 pago |
| B | Landings provincia | O2, O4 | 3 landings optimizadas (título+precio+CTA+trust) |
| C | Legal | O6 | Aviso legal unificado, canonical correcto |
| D | Contenido local + RD 659 | O3 | 2-3 artículos locales provincias sin técnico |
| E | Captación técnicos | O5 | +5 provincias con técnicos captados |

## Secuencia de verificación
1. Cada agente verifica su entregable LIVE antes de reportar.
2. Cástor verifica los entregables de todos (curl, SQL, navegador).
3. Deploy web: push main + verificación www.certificadoya.es (CDN 30-90s).
4. Métricas O2/O3 se miden en GSC/GoatCounter en 28d (cron semanal).

## Riesgos
- Cuota Resend (~100/día) limita recordatorios por email → SMS vía teléfono directo como fallback.
- Deploy sin Docker: usar `npx supabase functions deploy <fn> --project-ref wypgqpgjlookbhuaiyxa`.
- NUNCA `git add -A`; NUNCA tocar instalación Hermes.
