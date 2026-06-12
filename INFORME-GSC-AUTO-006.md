# INFORME-GSC-AUTO-006 — Automatización Google Search Console

**Fecha:** 2026-06-12  
**Tarea:** GSC-AUTO-006  
**Estado:** ✅ COMPLETADA

---

## G0: Verificación de credenciales

```
$ python3 -c "
import json
with open('/home/arturo/.credenciales/gsc-certificadoya.json') as f:
    data = json.load(f)
print('Email:', data.get('client_email', 'NO ENCONTRADO'))
print('Proyecto:', data.get('project_id', 'NO ENCONTRADO'))
"
✅ JSON válido
Email: gsc-notificador@certificadoya-seo.iam.gserviceaccount.com
Proyecto: certificadoya-seo
```

**Dependencias:** google-auth + requests instalados.

---

## G1: Creación de `herramientas/notificar_gsc.py`

Script que usa ADC (Application Default Credentials) con `GOOGLE_CLOUD_QUOTA_PROJECT=certificadoya-seo` para autenticarse como `artbriher@gmail.com` (Propietario en Search Console).

**Prueba en vivo:**
```
$ python3 herramientas/notificar_gsc.py
GSC OK — sitemap enviado a sc-domain:certificadoya.es (HTTP 204)
```

**Commit:** `2286c0c GSC-AUTO-1: script notificar_gsc.py` → push a origin/main ✅

---

## G2: Modificación de `herramientas/desplegar.sh`

Script que orquesta:
1. `git push`
2. `python3 notificar_indexnow.py`
3. `python3 notificar_gsc.py`

**Prueba en vivo:**
```
$ bash herramientas/desplegar.sh
=== DESPLIEGUE: push a GitHub ===
Everything up-to-date
=== NOTIFICAR IndexNow ===
ENVIADAS 137 URLs — HTTP 200
IndexNow OK
=== NOTIFICAR Google Search Console ===
GSC OK — sitemap enviado a sc-domain:certificadoya.es (HTTP 204)
GSC OK
=== DESPLIEGUE COMPLETO ===
```

**Commit:** `8b5c495 GSC-AUTO-2: orquestador desplegar.sh` → push a origin/main ✅

---

## G3: Regla permanente

Se ha añadido regla: **Siempre que se despliegue certificadoya.es, ejecutar `bash herramientas/desplegar.sh`** (incluye IndexNow + GSC).

---

## Resumen

| Fase | Estado | Detalle |
|------|--------|---------|
| G0 | ✅ | Credenciales OK, ADC configurado con quota_project |
| G1 | ✅ | `notificar_gsc.py` creado, HTTP 204 |
| G2 | ✅ | `desplegar.sh` creado, ambos notificadores OK |
| G3 | ✅ | Informe generado, regla establecida |

**Nota:** La autenticación usa ADC (`artbriher@gmail.com`) y requiere `GOOGLE_CLOUD_QUOTA_PROJECT=certificadoya-seo` en el entorno. Ver `notificar_gsc.py:obtener_token()`.
