#!/usr/bin/env python3
"""Send SEO report via Telegram - reads LAST token from .env file."""
import os, json, urllib.request

env_path = os.path.expanduser("/home/arturo/.hermes/.env")
token = None
with open(env_path) as f:
    for line in f:
        raw = line.rstrip('\n')
        if not raw:
            continue
        if raw.startswith('TELEGRAM_BOT_TOKEN='):
            val = raw.split('=', 1)[1].strip()
            if val:
                token = val

if not token:
    print("ERROR: TELEGRAM_BOT_TOKEN not found in .env")
    exit(1)

CHAT_ID = "308824075"

msg_lines = [
    "\U0001f4ca INFORME SEO \u2014 CertificadoYa.es",
    "\U0001f4c5 30 de mayo 2026, 12:00 UTC",
    "",
    "\U0001f50d TECNICO",
    "\u2022 Velocidad: Home 0.065s | Blog 0.210s | Articulo 0.174s | Provincia 0.054s",
    "\u2022 Sitemap: 154 URLs (30 blog + 124 provinciales)",
    "\u2022 SSL: OK",
    "\u2022 Meta tags: OK (5/5, 0 errores)",
    "\u2022 Blog coverage: 30 en sitemap, 29 en blog index (falta 1)",
    "\u2022 Enlaces rotos: 0 (20 revisados)",
    "\u2022 Puntuacion SEO: 100/100",
    "",
    "\U0001f4c8 SEARCH CONSOLE (16-30 mayo 2026)",
    "\u2022 Impresiones totales: 466 (+14.5% vs 407 anterior)",
    "\u2022 Clicks totales: 16 (+1)",
    "\u2022 Posicion media: 58.8 (mejora vs 59.3)",
    "",
    "Top 5 queries mas impresiones:",
    '  1. "auditoria energetica precio alicante" \u2014 7 imp, pos 67.1',
    '  2. "calificacion energetica alicante" \u2014 6 imp, pos 71.5',
    '  3. "auditoria eficiencia energetica alicante" \u2014 5 imp, pos 80.8',
    '  4. "cee asturias" \u2014 2 imp, pos 15.5',
    '  5. "ahorro energetico las palmas" \u2014 1 imp, pos 64.0',
    "",
    "Top queries mejor posicion (<30):",
    '  1. "cee asturias" \u2014 pos 15.5 (2 imp)',
    '  2. "cee bizkaia" \u2014 pos 18.0 (1 imp)',
    '  3. "cee bilbao" \u2014 pos 24.0 (2 imp)',
    "",
    "\u26a0 ALERTAS",
    "\u2022 Blog: 0.063s -> 0.210s (aumento 3.3x)",
    "\u2022 Home: 0.108s -> 0.065s (mejora 40%)",
    "\u2022 Search Console: +59 imp, +1 click (crecimiento)",
    "\u2022 Blog coverage: 1 articulo en sitemap no aparece en blog index",
    "\u2714 Sin URLs 404. Sitemap estable.",
    "",
    "_Generado por Hermes Agent_"
]
msg = "\n".join(msg_lines)

payload = json.dumps({"chat_id": CHAT_ID, "text": msg}).encode()
req = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data=payload, method="POST"
)
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req, timeout=15) as resp:
    result = json.loads(resp.read())
    print(f"Telegram OK: {result['ok']}")
    if result.get("result"):
        print(f"Message ID: {result['result']['message_id']}")