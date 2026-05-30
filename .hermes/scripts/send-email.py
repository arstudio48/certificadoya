#!/usr/bin/env python3
"""Send email via Gmail SMTP."""
import smtplib
from email.message import EmailMessage

SMTP_USER = "arturobriher@gmail.com"
SMTP_PASS = "tlmf yzzq rqmg jcko"

msg = EmailMessage()
msg['From'] = "arturobriher@gmail.com"
msg['To'] = "aparejado@me.com"
msg['Subject'] = "Informe SEO CertificadoYa - 30 mayo 2026"

body = """[INFORME SEO - CertificadoYa.es]
[30 de mayo 2026, 12:00 UTC]

-- TECNICO --
- Velocidad: Home 0.065s, Blog 0.210s, Articulo 0.174s, Provincia 0.054s
- Sitemap: 154 URLs (30 blog + 124 provinciales)
- SSL: OK
- Meta tags: OK (5/5, 0 errores)
- Blog coverage: 30 en sitemap, 29 en blog index (falta 1)
- Enlaces rotos: 0 (20 revisados)
- Puntuacion SEO: 100/100

-- SEARCH CONSOLE (16-30 mayo 2026) --
- Impresiones totales: 466 (+14.5% vs 407 anterior)
- Clicks totales: 16 (+1)
- Posicion media: 58.8 (mejora vs 59.3)

Top 5 queries mas impresiones:
  1. auditoria energetica precio alicante - 7 imp, pos 67.1
  2. calificacion energetica alicante - 6 imp, pos 71.5
  3. auditoria eficiencia energetica alicante - 5 imp, pos 80.8
  4. cee asturias - 2 imp, pos 15.5
  5. ahorro energetico las palmas - 1 imp, pos 64.0

Top queries mejor posicion:
  1. cee asturias - pos 15.5 (2 imp)
  2. cee bizkaia - pos 18.0 (1 imp)
  3. cee bilbao - pos 24.0 (2 imp)

-- ALERTAS --
- Blog: 0.063s -> 0.210s (aumento 3.3x)
- Home: 0.108s -> 0.065s (mejora 40%)
- Search Console: +59 imp, +1 click (crecimiento)
- Blog coverage: 1 articulo en sitemap no aparece en blog index
- Sin URLs 404. Sitemap estable.

Generado por Hermes Agent"""

msg.set_content(body)

with smtplib.SMTP('smtp.gmail.com', 587) as s:
    s.starttls()
    s.login(SMTP_USER, SMTP_PASS)
    s.send_message(msg)
    print("Email sent OK")