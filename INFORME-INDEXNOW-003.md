# INFORME-INDEXNOW-003

**Proyecto:** certificadoya.es · **Fecha:** 2026-06-12 · **Estado:** COMPLETADO ✅

---

## I1 — Publicar fichero de clave ✅

```
$ curl -s https://www.certificadoya.es/6bb26488e25424884ad59eb43644e538.txt
6bb26488e25424884ad59eb43644e538
```

Commit `INDEXNOW-1: publicar clave` → `0b369d9` → push → 90s espera → live ✅

---

## I2 — Envío inicial de 138 URLs del sitemap ✅

```
$ wc -l /tmp/urls_indexnow.txt
138 /tmp/urls_indexnow.txt
```

```
$ python3 -c "..."  # lote completo a api.indexnow.org
HTTP 202
```

138 URLs enviadas, HTTP 202 (Accepted) ✅

---

## I3 — Script permanente `herramientas/notificar_indexnow.py` ✅

```
$ python3 herramientas/notificar_indexnow.py https://www.certificadoya.es/
ENVIADAS 1 URLs — HTTP 200
```

**Instrucción de uso:**  
Tras cada despliegue con páginas nuevas o modificadas, ejecutar  
`python3 herramientas/notificar_indexnow.py <urls...>`  
Sin argumentos, envía todas las URLs del sitemap.

Commit `INDEXNOW-3: script permanente` → `8ac7565` → push ✅

---

## Resumen final

| Fase | Resultado |
|------|-----------|
| I1 — Clave publicada | `6bb26488e25424884ad59eb43644e538.txt` accesible en raíz ✅ |
| I2 — Lote inicial | 138 URLs → HTTP 202 ✅ |
| I3 — Script permanente | `herramientas/notificar_indexnow.py` operativo ✅ |
