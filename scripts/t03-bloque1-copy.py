#!/usr/bin/env python3
"""
T0.3 — Bloque 1: Corrección integral de copy.
1.1: Precios desde 45€/35€ → desde 60€
1.2: Plazo 24h → 48-72h (salvo urgente)
1.3: Eliminar claims 4,9★
"""

import os
import re

BASE = '/home/arturo/certificadoya'
EXCLUDE = {'node_modules', '.git', '__pycache__'}
SKIP = {'apply_overlay_menu.py', 'accordion-overlay.py', 't03-bloque1-copy.py'}

def find_html():
    files = []
    for root, dirs, names in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        for f in names:
            if f.endswith('.html') and f not in SKIP:
                files.append(os.path.join(root, f))
    return files

def fix_45(content):
    """45€ → 60€ en tarjeta precio, titles, metas, schema, texto"""
    c = 0
    # Tarjeta de precio principal
    content, n = re.subn(
        r'(font-size:2\.4rem;font-weight:800;color:#16a34a;line-height:1\.1">)45(<)',
        r'\1>60<', content)  # wait, this doesn't make sense
    c += n
    return content, c

# Let me be more careful
def fix_all(content, path):
    changes = []
    
    # === 1. PRECIO: 45€ → 60€ ===
    # Tarjeta precio hero: >45< dentro del span de precio
    content, n = re.subn(
        r'(font-size:2\.4rem;font-weight:800;color:#16a34a;line-height:1\.1">)45(<span)',
        r'\g<1>60\g<2>', content)
    if n: changes.append(f'tarjeta-precio-45→60: {n}')
    
    # "desde 45€" → "desde 60€"
    content, n = re.subn(r'desde\s+45(\s*€)', r'desde 60\g<1>', content)
    if n: changes.append(f'desde-45€→60€: {n}')
    
    # "desde 45" seguido de párrafo/salto
    content, n = re.subn(r'desde\s+45([\s.,;:!?\)<])', r'desde 60\g<1>', content)
    if n: changes.append(f'desde-45→60: {n}')
    
    # Rangos "45-70€", "45-80€", "45-55€" en FAQ/precios
    def bump_range(m):
        start = m.group(1)
        end = int(m.group(2)) + 20
        return f'{start}60-{end}'
    content, n = re.subn(
        r'(oscila entre <strong>)45-(\d+)',
        bump_range, content)
    if n: changes.append(f'rango-45→60: {n}')
    
    # Tabla precios "45-55" en Badajoz-style
    def bump_table(m):
        end = int(m.group(1)) + 25
        return f'60-{end}'
    content, n = re.subn(r'45-(\d+)€', bump_table, content)
    if n: changes.append(f'tabla-45→60: {n}')
    
    # === 2. PRECIO: 35€ → 60€ (Badajoz) ===
    # Tarjeta precio hero 35
    content, n = re.subn(
        r'(font-size:2\.4rem;font-weight:800;color:#16a34a;line-height:1\.1">)35(<span)',
        r'\g<1>60\g<2>', content)
    if n: changes.append(f'tarjeta-precio-35→60: {n}')
    
    content, n = re.subn(r'desde\s+35(\s*€)', r'desde 60\g<1>', content)
    if n: changes.append(f'desde-35€→60€: {n}')
    
    content, n = re.subn(r'desde\s+35([\s.,;:!?\)<])', r'desde 60\g<1>', content)
    if n: changes.append(f'desde-35→60: {n}')
    
    # Rangos "35-55€" en Badajoz
    def bump_range35(m):
        end = int(m.group(1)) + 25
        return f'60-{end}'
    content, n = re.subn(r'(oscila entre <strong>)35-(\d+)', 
        lambda m: f'{m.group(1)}60-{int(m.group(2))+25}', content)
    if n: changes.append(f'rango-35→60: {n}')
    
    # Tabla Badajoz "35-55" 
    content, n = re.subn(r'35-(\d+)', 
        lambda m: f'60-{int(m.group(1))+25}', content)
    if n: changes.append(f'tabla-35→60: {n}')
    
    # === 3. PLAZO: 24h → 48-72h (excepto urgente) ===
    if 'urgente' not in path.lower():
        # "en 24h" → "en 48-72h"
        content, n = re.subn(r'en\s+24\s*h', 'en 48-72h', content)
        if n: changes.append(f'en-24h→48-72h: {n}')
        
        # "24-48h" → "48-72h"
        content, n = re.subn(r'24-48(\s*h)', r'48-72\g<1>', content)
        if n: changes.append(f'24-48h→48-72h: {n}')
        
        # Titles: "Presupuesto en 24h | Desde"
        content, n = re.subn(
            r'(Presupuesto\s+en\s+)24(\s*h)',
            r'\g<1>48-72\g<2>', content)
        if n: changes.append(f'presupuesto-24h→48-72h: {n}')
        
        # "| 24h" en titles
        content, n = re.subn(
            r'\|.*?24\s*h[^<]*',
            lambda m: m.group(0).replace('24', '48-72'), content)
        if n: changes.append(f'title-24h→48-72h: {n}')
    
    # === 4. CLAIMS: 4,9★ ===
    # Eliminar trust-item con 4,9★
    content, n = re.subn(
        r'\s*<div class="trust-item">\s*'
        r'<svg[^>]*>.*?</svg>\s*'
        r'4,9\s*★[^<]*</div>',
        '', content)
    if n: changes.append(f'claim-4,9★: {n}')
    
    return content, changes

def main():
    files = find_html()
    print(f"🔍 {len(files)} archivos HTML")
    
    all_changes = {}
    modified = 0
    
    for path in files:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        content, changes = fix_all(content, path)
        
        if content != original:
            rel = os.path.relpath(path, BASE)
            all_changes[rel] = changes
            modified += 1
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            ch_str = '; '.join(changes)
            print(f"  ✓ {rel}")
            print(f"    → {ch_str}")
    
    print(f"\n{'='*50}")
    print(f"📊 Archivos modificados: {modified}")
    for rel, ch in sorted(all_changes.items()):
        print(f"  {rel}: {'; '.join(ch)}")

if __name__ == '__main__':
    main()
