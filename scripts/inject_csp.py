#!/usr/bin/env python3
"""
Inject CSP meta tag into all HTML files of certificadoya.es (byte-exact).
Inserta <meta http-equiv="Content-Security-Policy"> just after <head> if absent.
Trabaja en bytes: preserva exactamente CRLF/LF/UTF-8 originales del archivo -> diff minimo (1 linea por archivo).

Uso: python3 scripts/inject_csp.py [--dry-run]
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.git', 'node_modules', '.github', 'supabase', 'scripts', '_scripts',
             'workers', 'herramientas', 'data', 'datos', 'facturas', 'instancias',
             'propuestas', 'prototipos', 'reserva', 'venv_new', '__pycache__',
             'informes', 'analytics', '.hermes'}

# Politica construida desde la auditoria de recursos externos (2026-08-08)
CSP = ("default-src 'self'; "
       "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com "
       "https://gc.zgo.at https://unpkg.com https://cdn.jsdelivr.net "
       "https://static.licdn.com https://platform.linkedin.com; "
       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com "
       "https://fonts.gstatic.com https://static.licdn.com https://unpkg.com; "
       "img-src 'self' data: https:; "
       "font-src 'self' data: https://fonts.googleapis.com https://fonts.gstatic.com; "
       "connect-src 'self' https://wypgqpgjlookbhuaiyxa.supabase.co "
       "https://certificadoya.goatcounter.com https://gc.zgo.at "
       "https://www.google-analytics.com https://analytics.google.com "
       "https://www.googletagmanager.com https://clarity.ms https://*.clarity.ms "
       "https://www.linkedin.com https://*.licdn.com https://platform.linkedin.com; "
       "frame-src 'self' https://www.googletagmanager.com; "
       "object-src 'none'; base-uri 'self'; "
       "form-action 'self' https://wypgqpgjlookbhuaiyxa.supabase.co")

META = '<meta http-equiv="Content-Security-Policy" content="%s">' % CSP


def html_files():
    out = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.lower().endswith(('.html', '.htm')):
                out.append(os.path.join(root, f))
    return sorted(out)


def main():
    dry = '--dry-run' in sys.argv
    changed, already, nohead = 0, 0, 0
    for fp in html_files():
        with open(fp, 'rb') as fh:
            data = fh.read()
        if b'Content-Security-Policy' in data:
            already += 1
            continue
        m = re.search(rb'<head[^>]*>', data, re.I)
        if not m:
            nohead += 1
            continue
        newline = b'\r\n' if b'\r\n' in data else b'\n'
        pos = m.end()
        data = data[:pos] + newline + META.encode('utf-8') + newline + data[pos:]
        if not dry:
            with open(fp, 'wb') as fh:
                fh.write(data)
        changed += 1
    print(f"CSP {'DRY-RUN: ' if dry else ''}lista -> {changed} modificados, {already} ya tenian, {nohead} sin <head>")


if __name__ == '__main__':
    main()