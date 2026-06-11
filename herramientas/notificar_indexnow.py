#!/usr/bin/env python3
"""
notificar_indexnow.py — Notifica URLs nuevas/modificadas a IndexNow (Bing, Yandex, etc.)
Tras cada despliegue, ejecutar: python3 herramientas/notificar_indexnow.py [urls...]
Sin argumentos, envía todas las URLs del sitemap.
"""

import json, sys, urllib.request

CLAVE = "6bb26488e25424884ad59eb43644e538"
SITIO = "www.certificadoya.es"
ENDPOINT = "https://api.indexnow.org/indexnow"

def leer_sitemap():
    import xml.etree.ElementTree as ET
    tree = ET.parse("sitemap.xml")
    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for loc in tree.findall(".//ns:loc", ns):
        texto = loc.text
        if texto:
            urls.append(texto.strip())
    return urls

def notificar(urls):
    if not urls:
        print("ERROR: lista de URLs vacía")
        sys.exit(1)
    cuerpo = json.dumps({
        "host": SITIO,
        "key": CLAVE,
        "keyLocation": f"https://{SITIO}/{CLAVE}.txt",
        "urlList": urls
    }).encode()
    pet = urllib.request.Request(ENDPOINT, data=cuerpo,
        headers={"Content-Type": "application/json; charset=utf-8"})
    resp = urllib.request.urlopen(pet, timeout=30)
    print(f"ENVIADAS {len(urls)} URLs — HTTP {resp.status}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        urls = leer_sitemap()
    notificar(urls)
