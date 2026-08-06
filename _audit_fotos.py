#!/usr/bin/env python3
"""
GUARDA CERO-REPETICIONES del blog de CertificadoYa.
Verifica que NINGUNA foto de contenido (img/blog/tema-*.jpg, *.jpg/.png/.webp)
esta repetida: ni entre articulos, ni internamente en el index, ni en solape
index<->articulo. NO genera ninguna foto (solo comprueba).
Uso: python _audit_fotos.py  -> sale con codigo 0 si OK, 1 si hay repetidas.
"""
import os, re, glob, sys
from collections import defaultdict, Counter

REPO = os.path.dirname(os.path.abspath(__file__))
blogdir = os.path.join(REPO, "blog")

UI = ('ico-', 'logo', 'favicon', 'og-image', 'arrow', 'check', 'whatsapp',
      'bg-', 'pattern', 'icon', 'placeholder', 'ui-', 'btn', 'apple-touch', 'autor-')

def is_content(im):
    b = im.lower().split('/')[-1]
    if b.startswith('autor-'): return False
    if any(p in b for p in UI): return False
    if b.endswith('.svg'): return False  # graficos de diseno (etiqueta energetica, iconos) no son fotos
    return im.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))

def fotos_archivo(path):
    hh = open(path, encoding='utf-8', errors='ignore').read()
    return [im for im in re.findall(r'src="(/img/[^"]+)"', hh) if is_content(im)]

problems = []

# 1) Repeticiones entre articulos (misma foto en 2+ articulos)
inv = defaultdict(set)
for fn in os.listdir(blogdir):
    if not fn.endswith('.html') or fn == 'index.html': continue
    for im in fotos_archivo(os.path.join(blogdir, fn)):
        inv[im].add(fn)
for im, arts in inv.items():
    if len(arts) > 1:
        problems.append(f"REPETIDA ENTRE ARTICULOS: {im} -> {len(arts)} articulos")

# 2) Index internas
ih = open(os.path.join(blogdir, "index.html"), encoding='utf-8', errors='ignore').read()
ci = Counter(re.findall(r'src="(/img/[^"]+)"', ih))
for k, v in ci.items():
    if v > 1 and is_content(k):
        problems.append(f"DUPLICADA EN INDEX: {k} aparece {v} veces")

# 3) Solape index<->articulo
idx_set = set(re.findall(r'src="(/img/[^"]+)"', ih))
for fn in os.listdir(blogdir):
    if not fn.endswith('.html') or fn == 'index.html': continue
    for im in fotos_archivo(os.path.join(blogdir, fn)):
        if im in idx_set:
            problems.append(f"SOLAPE INDEX<->ARTICULO: {im} en {fn} y en index")

if problems:
    print("❌ HAY FOTOS REPETIDAS:", len(problems))
    for p in problems[:30]: print("  ", p)
    sys.exit(1)
else:
    print("✅ OK: 0 fotos repetidas en todo el blog (articulos + index).")
    sys.exit(0)
