#!/usr/bin/env python3
"""SEO Analyzer for CertificadoYa — Weekly Technical SEO Report"""
import json, subprocess, sys, time
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError

SITE = "https://www.certificadoya.es"
REPORT = {}

def curl(url, timeout=15):
    try:
        start = time.time()
        r = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=timeout)
        content = r.read()
        elapsed = time.time() - start
        return {"status": r.status, "size": len(content), "time": round(elapsed, 3), "content": content}
    except Exception as e:
        return {"status": 0, "error": str(e), "time": 0, "size": 0, "content": b""}

print("🔍 SEO Analyzer — CertificadoYa")
print(f"📅 {datetime.now().isoformat()}\n")

# 1. SPEED
print("1️⃣  Velocidad...")
pages = {
    "Home": "/",
    "Blog": "/blog/",
    "Artículo": "/blog/guia-ce3x-tecnicos.html",
    "Provincia": "/certificado-energetico-madrid/",
}
REPORT["speed"] = {}
for name, path in pages.items():
    r = curl(SITE + path)
    REPORT["speed"][name] = {"status": r["status"], "time_s": r["time"], "size_kb": round(r["size"]/1024, 1)}
    status_icon = "✅" if r["status"] == 200 else ("⚠️" if r["status"] else "❌")
    print(f"  {status_icon} {name}: {r['time']}s | {round(r['size']/1024,1)}KB")

# 2. SITEMAP
print("\n2️⃣  Sitemap...")
r = curl(SITE + "/sitemap.xml")
if r["status"] == 200:
    url_count = r["content"].decode().count("<url>")
    REPORT["sitemap"] = {"status": "ok", "urls": url_count, "size_kb": round(r["size"]/1024, 1)}
    print(f"  ✅ {url_count} URLs | {round(r['size']/1024,1)}KB")
else:
    REPORT["sitemap"] = {"status": "error", "error": r.get("error", "HTTP " + str(r["status"]))}
    print(f"  ❌ Error: {r.get('error', r['status'])}")

# 3. ROBOTS.TXT
print("\n3️⃣  Robots.txt...")
r = curl(SITE + "/robots.txt")
if r["status"] == 200:
    REPORT["robots"] = {"status": "ok"}
    print(f"  ✅ {len(r['content'].decode().split(chr(10)))} líneas")
else:
    REPORT["robots"] = {"status": "error"}
    print(f"  ❌ Error")

# 4. SSL
print("\n4️⃣  SSL...")
r = curl(SITE)
if r["status"] == 200:
    REPORT["ssl"] = {"status": "ok"}
    print("  ✅ SSL válido")
else:
    REPORT["ssl"] = {"status": "error"}
    print("  ❌ SSL problem")

# 5. META TAGS (sample articles)
print("\n5️⃣  Meta tags (muestra)...")
sample_articles = [
    "/blog/guia-ce3x-tecnicos.html",
    "/blog/precio-certificado-energetico-2026.html",
    "/blog/normativa-cee-2026.html",
    "/certificado-energetico-madrid/",
    "/certificado-energetico-barcelona/",
]
REPORT["meta"] = {"checked": 0, "errors": []}
for path in sample_articles:
    r = curl(SITE + path)
    if r["status"] != 200:
        REPORT["meta"]["errors"].append(f"{path}: HTTP {r['status']}")
        continue
    html = r["content"].decode("utf-8", errors="ignore")
    issues = []
    if "<title>" not in html: issues.append("Sin title")
    if 'meta name="description"' not in html and 'meta property="description"' not in html:
        issues.append("Sin description")
    if 'rel="canonical"' not in html: issues.append("Sin canonical")
    if 'og:title' not in html: issues.append("Sin og:title")
    if 'twitter:card' not in html: issues.append("Sin twitter:card")
    if issues:
        REPORT["meta"]["errors"].append(f"{path}: {', '.join(issues)}")
        print(f"  ❌ {path}: {', '.join(issues)}")
    else:
        print(f"  ✅ {path}")
    REPORT["meta"]["checked"] += 1

# 6. REDIRECTS
print("\n6️⃣  Redirecciones...")
r = curl("https://certificadoya.es/", timeout=10)
final_url = r.get("final_url", SITE)
REPORT["redirect"] = {"status": "ok" if r["status"] == 200 else "error"}
print(f"  ✅ {r['status']} → {SITE}" if r["status"] == 200 else f"  ❌ {r.get('error', r['status'])}")

# 7. BROKEN LINKS (sample)
print("\n7️⃣  Enlaces internos (muestra)...")
r = curl(SITE + "/blog/")
if r["status"] == 200:
    html = r["content"].decode("utf-8", errors="ignore")
    import re
    links = re.findall(r'href=["\']([^"\']+\.html)["\']', html)
    broken = []
    for link in links[:20]:
        url = SITE + link if link.startswith("/") else link
        lr = curl(url, timeout=10)
        if lr["status"] != 200:
            broken.append(link)
    REPORT["links"] = {"checked": min(len(links), 20), "broken": broken}
    print(f"  ✅ {min(len(links), 20)} enlaces revisados" if not broken else f"  ❌ {len(broken)} rotos: {broken[:3]}")

# SUMMARY
print("\n" + "="*50)
print("📊 RESUMEN")
print("="*50)
bad = 0
for k, v in REPORT.items():
    if isinstance(v, dict):
        s = v.get("status", "ok")
        if s == "error" or (k == "meta" and v.get("errors")):
            bad += 1
            print(f"❌ {k.upper()}: MAL")
        else:
            print(f"✅ {k.upper()}: BIEN")

score = round((1 - bad / max(len(REPORT), 1)) * 100)
REPORT["score"] = score
REPORT["timestamp"] = datetime.now().isoformat()

print(f"\n🏆 Puntuación SEO técnica: {score}/100")

# Save
with open("/home/arturo/.hermes/home/seo-report.json", "w") as f:
    json.dump(REPORT, f, indent=2)
print("\n✅ Informe guardado en ~/.hermes/home/seo-report.json")

# Output for cron delivery
if score < 70:
    print(f"\n⚠️  ALERTA: Puntuación baja ({score}). Revisar issues.")
