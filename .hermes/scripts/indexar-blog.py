#!/usr/bin/env python3
"""Indexar nuevos artículos en buscadores."""
import urllib.request
import json
import sys

domain = "https://www.certificadoya.es"
sitemap = f"{domain}/sitemap.xml"
indexnow_key = "6a78e2e987818fc3ba8f73e23bfe8ada.txt"
indexnow_host = "www.certificadoya.es"

# Nuevas URLs de este lote
urls = [
    "https://www.certificadoya.es/blog/ultimos-dias-ayudas-20000-euros-rehabilitacion-2026.html"
]

ok = True

# 1. Google sitemap ping
try:
    req = urllib.request.Request(
        f"https://www.google.com/ping?sitemap={sitemap}",
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        print(f"✅ Google sitemap ping: {r.status}")
except Exception as e:
    print(f"❌ Google sitemap ping: {e}")
    ok = False

# 2. Bing IndexNow (lote)
try:
    body = json.dumps({
        "host": indexnow_host,
        "key": indexnow_key.replace(".txt", ""),
        "keyLocation": f"{domain}/{indexnow_key}",
        "urlList": urls,
    }).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        print(f"✅ Bing/IndexNow: {r.status}")
except Exception as e:
    print(f"❌ Bing/IndexNow: {e}")
    ok = False

# 3. Yandex sitemap ping
try:
    req = urllib.request.Request(
        f"https://webmaster.yandex.com/ping?sitemap={sitemap}",
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        print(f"✅ Yandex: {r.status}")
except Exception as e:
    print(f"❌ Yandex: {e}")
    ok = False

sys.exit(0 if ok else 1)
