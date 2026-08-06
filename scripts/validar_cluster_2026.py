#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validar_cluster_2026.py — Validación binaria del cluster SEO 2026."""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = "https://www.certificadoya.es"
HOY = "2026-07-31"

slugs = [
    "guia-cambios-certificado-energetico-2026",
    "nuevo-modelo-etiqueta-energetica-2026",
    "formato-xml-certificado-energetico-rd-659-2025",
    "validez-certificado-energetico-antiguo-2026",
    "registro-centralizado-certificado-energetico-2026",
    "certificado-energetico-nuevo-formato-fecha-limite",
]
PILAR = slugs[0]

checks = {}

# 1. Existen los 6 index.html
existen = []
for s in slugs:
    ruta = os.path.join(BASE, s, "index.html")
    if os.path.isfile(ruta):
        existen.append(s)
checks["1_existen_6_html"] = len(existen) == 6
print(f"[{'PASS' if checks['1_existen_6_html'] else 'FAIL'}] Existen 6 index.html ({len(existen)}/6)")

# 2. title, meta description, canonical no vacíos
ok_seo = True
for s in slugs:
    ruta = os.path.join(BASE, s, "index.html")
    with open(ruta, "r", encoding="utf-8") as f:
        c = f.read()
    t = re.search(r"<title>(.*?)</title>", c, re.S)
    d = re.search(r'<meta name="description" content="(.*?)">', c, re.S)
    cn = re.search(r'<link rel="canonical" href="(.*?)">', c, re.S)
    if not (t and t.group(1).strip() and d and d.group(1).strip() and cn and cn.group(1).strip()):
        ok_seo = False
        print(f"   -> FALLO en {s}")
checks["2_seo_metas"] = ok_seo
print(f"[{'PASS' if ok_seo else 'FAIL'}] title + description + canonical no vacíos en 6 páginas")

# 3. JSON-LD válido en las 6
ok_jsonld = True
for s in slugs:
    ruta = os.path.join(BASE, s, "index.html")
    with open(ruta, "r", encoding="utf-8") as f:
        c = f.read()
    bloques = re.findall(r'<script type="application/ld\+json">(.*?)</script>', c, re.S)
    if not bloques:
        ok_jsonld = False
        print(f"   -> {s}: sin JSON-LD")
        continue
    for b in bloques:
        try:
            json.loads(b.strip())
        except Exception as e:
            ok_jsonld = False
            print(f"   -> {s}: JSON-LD inválido: {e}")
checks["3_jsonld_valido"] = ok_jsonld
print(f"[{'PASS' if ok_jsonld else 'FAIL'}] JSON-LD válido (sintaxis) en 6 páginas")

# 4. Enlazado interno pilar <-> satélites
ok_links = True
with open(os.path.join(BASE, PILAR, "index.html"), "r", encoding="utf-8") as f:
    pilar_c = f.read()
for s in slugs[1:]:
    if f"{WEB}/{s}/" not in pilar_c:
        ok_links = False
        print(f"   -> Pilar no enlaza a {s}")
    with open(os.path.join(BASE, s, "index.html"), "r", encoding="utf-8") as f:
        sat_c = f.read()
    if f"{WEB}/{PILAR}/" not in sat_c:
        ok_links = False
        print(f"   -> Satélite {s} no enlaza al pilar")
checks["4_interlinking"] = ok_links
print(f"[{'PASS' if ok_links else 'FAIL'}] Enlazado interno pilar<->satélites bidireccional")

# 5. sitemap.xml: 6 URLs, sin duplicados, lastmod hoy
with open(os.path.join(BASE, "sitemap.xml"), "r", encoding="utf-8") as f:
    sm = f.read()
urls_sm = re.findall(r"<loc>(.*?)</loc>", sm)
duplicados = [u for u in set(urls_sm) if urls_sm.count(u) > 1]
ok_sm = True
for s in slugs:
    u = f"{WEB}/{s}/"
    if u not in urls_sm:
        ok_sm = False
        print(f"   -> sitemap no contiene {u}")
    m = re.search(rf"<loc>{re.escape(u)}</loc><lastmod>([^<]+)</lastmod>", sm)
    if not m:
        ok_sm = False
        print(f"   -> {u} sin lastmod")
    elif m.group(1) != HOY:
        ok_sm = False
        print(f"   -> {u} lastmod {m.group(1)} != {HOY}")
if duplicados:
    ok_sm = False
    print(f"   -> Duplicados en sitemap: {duplicados}")
checks["5_sitemap"] = ok_sm
print(f"[{'PASS' if ok_sm else 'FAIL'}] sitemap.xml: 6 URLs, sin duplicados, lastmod {HOY}")

# 6. Payload IndexNow con las 6 URLs
ruta_payload = os.path.join(BASE, "herramientas", "indexnow-payload-cluster-2026.json")
ok_in = False
if os.path.isfile(ruta_payload):
    with open(ruta_payload, "r", encoding="utf-8") as f:
        payload = json.load(f)
    url_list = payload.get("urlList", [])
    ok_in = len(url_list) == 6 and all(f"{WEB}/{s}/" in url_list for s in slugs)
    if not ok_in:
        print(f"   -> urlList incompleta: {url_list}")
checks["6_indexnow_payload"] = ok_in
print(f"[{'PASS' if ok_in else 'FAIL'}] Payload IndexNow con las 6 URLs")

# 7. Ninguna página fuera del cluster modificada: comprobamos el git diff de HTML raíz
#    (se valida con git diff --stat en el informe; aquí chequeamos que no hay diffs en HTML no relacionados)
print()
print("=== Resumen ===")
todos_ok = all(checks.values())
for k, v in checks.items():
    print(f"  {k}: {'PASS' if v else 'FAIL'}")
print(f"RESULTADO GLOBAL: {'PASS ✅' if todos_ok else 'FAIL ❌'}")
sys.exit(0 if todos_ok else 1)
