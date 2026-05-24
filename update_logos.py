#!/usr/bin/env python3
import os

old_logo = '<a href="/" class="logo">⚡ Certificado<span>Ya</span></a>'
new_logo = '''<a href="/" class="logo">
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="32" height="32" rx="6" fill="#547c24"/>
        <text x="16" y="23" text-anchor="middle" fill="white" font-size="20" font-weight="700" font-family="Montserrat,sans-serif">C</text>
      </svg>
      <div class="logo-text-wrap">
        <span class="logo-text">Certificado<span class="logo-highlight">Ya</span></span>
        <span class="logo-sub">certificación energética de edificios existentes (CEE)</span>
      </div>
    </a>'''

files = [
    "aviso-legal.html", "cookies.html", "privacidad.html", "preview-movil.html",
    "organismos-contacto.html", "pago-exitoso.html",
    "legal/index.html", "legal/aviso-legal.html", "legal/privacidad.html", "legal/cookies.html"
]

for f in files:
    if not os.path.exists(f):
        print(f"⚠️  {f} - not found")
        continue
    with open(f) as fh:
        content = fh.read()
    if old_logo in content:
        content = content.replace(old_logo, new_logo)
        with open(f, 'w') as fh:
            fh.write(content)
        print(f"✅ {f}")
    else:
        print(f"⚠️  {f} - pattern not found")
