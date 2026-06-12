# INFORME-GSC-FIX-007

**Proyecto:** certificadoya.es  
**Fecha:** 2026-06-12  
**Motivo:** Corrección de GSC-AUTO-006 — ADC limitado a webmasters, sesiones revocadas

---

## R1 — Revocar ADC amplio anterior

```
$ /tmp/google-cloud-sdk/bin/gcloud auth application-default revoke --quiet
Credentials revoked.

$ rm -f /home/arturo/.hermes/home/.config/gcloud/application_default_credentials.json && echo BORRADO
BORRADO
```

✅ ADC anterior revocado y fichero eliminado.

---

## R2 — Crear ADC limitado a Search Console

```
$ /tmp/google-cloud-sdk/bin/gcloud auth application-default login --no-launch-browser \
    --scopes=openid,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/webmasters
```

**Código OAuth:** proporcionado por Arturo vía Telegram.  
**Resultado:**
```
Credentials saved to file: [/home/arturo/.hermes/home/.config/gcloud/application_default_credentials.json]
Quota project "certificadoya-seo" was added to ADC
```

✅ ADC creado con scopes: openid + cloud-platform + webmasters.  
✅ Quota project: certificadoya-seo.

---

## R3 — Adaptar notificar_gsc.py

El script ya usaba `google.auth.default(scopes=["https://www.googleapis.com/auth/webmasters"])`.  
Sin cambios necesarios.

---

## R4 — Prueba del script

```
$ python3 herramientas/notificar_gsc.py
GSC OK — sitemap enviado a sc-domain:certificadoya.es (HTTP 204)
```

✅ Script funcional con ADC limitado.

---

## R5 — Revocar sesiones gcloud normales

```
$ /tmp/google-cloud-sdk/bin/gcloud auth revoke --all --quiet
Revoked credentials:
 - artbriher@gmail.com
 - gsc-notificador@certificadoya-seo.iam.gserviceaccount.com
```

Verificación post-revocación:
```
$ python3 herramientas/notificar_gsc.py
GSC OK — sitemap enviado a sc-domain:certificadoya.es (HTTP 204)
```

✅ Sesiones revocadas. ADC sigue operativo sin sesiones de gcloud activas.

---

## R6 — desplegar.sh completo

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

✅ Despliegue extremo a extremo funcional.

---

## Tarea recurrente

Creado cron job semanal (lunes 10:00) recordando reintentar añadir la cuenta de servicio a GSC.

---

## Estado final

- ✅ ADC limitado solo a webmasters + cloud-platform
- ✅ Sesiones personales de gcloud revocadas
- ✅ `notificar_gsc.py` funcional (HTTP 204)
- ✅ `desplegar.sh` funcional (IndexNow + GSC)
- 🔄 Pendiente: cuando Google arregle el bug, reintentar añadir `gsc-notificador@certificadoya-seo.iam.gserviceaccount.com` a Search Console
