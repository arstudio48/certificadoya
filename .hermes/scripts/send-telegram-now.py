#!/usr/bin/env python3
"""Send SEO report via Telegram."""
import os, json, urllib.request

token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
chat_id = "308824075"

msg = (
    "📊 INFORME SEO — CertificadoYa.es\n"
    "📅 30 de mayo 2026, 12:00 UTC\n"
    "\n"
    "🔍 TÉCNICO\n"
    "• Velocidad: Home 0.065s | Blog 0.210s | Artículo 0.174s | Provincia 0.054s\n"
    "• Sitemap: 154 URLs (30 blog + 124 provinciales)\n"
    "• SSL: ✅ OK\n"
    "• Meta tags: ✅ OK (5/5, 0 errores)\n"
    "• Blog coverage: 30 en sitemap, 29 en blog index (falta 1)\n"
    "• Enlaces rotos: 0 (20 revisados)\n"
    "• Puntuación SEO: 100/100\n"
    "\n"
    "📈 SEARCH CONSOLE (16-30 mayo 2026)\n"
    "• Impresiones totales: 466 (+14.5% vs anterior 407)\n"
    "• Clicks totales: 16 (+1)\n"
    "• Posición media: 58.8 (mejora vs 59.3)\n"
    "\n"
    "Top 5 queries más impresiones:\n"
    "  1. \"auditoria energetica precio alicante\" — 7 imp, pos 67.1\n"
    "  2. \"calificacion energetica alicante\" — 6 imp, pos 71.5\n"
    "  3. \"auditoria eficiencia energetica alicante\" — 5 imp, pos 80.8\n"
    "  4. \"cee asturias\" — 2 imp, pos 15.5\n"
    "  5. \"ahorro energético las palmas\" — 1 imp, pos 64.0\n"
    "\n"
    "Top queries mejor posición (<30):\n"
    "  1. \"cee asturias\" — pos 15.5 (2 imp)\n"
    "  2. \"cee bizkaia\" — pos 18.0 (1 imp)\n"
    "  3. \"cee bilbao\" — pos 24.0 (2 imp)\n"
    "\n"
    "⚠️ ALERTAS\n"
    "• Blog: 0.063s → 0.210s (aumento de velocidad)\n"
    "• Home: 0.108s → 0.065s (mejora)\n"
    "• Search Console: +59 impresiones, +1 click (crecimiento)\n"
    "• Blog coverage: 1 artículo en sitemap no aparece en blog index\n"
    "✅ Sin URLs 404 nuevas. Sitemap estable.\n"
    "\n"
    "_Generado por Hermes Agent_"
)

payload = json.dumps({
    "chat_id": chat_id,
    "text": msg
}).encode()

req = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data=payload,
    method="POST"
)
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req, timeout=15) as resp:
    result = json.loads(resp.read())
    print(f"Telegram OK: {result['ok']}")
    if not result["ok"]:
        print(result)