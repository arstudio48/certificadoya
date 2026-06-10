#!/usr/bin/env python3
"""Añade .mobile-overlay{display:none!important} antes de /* Menú overlay móvil */
en todos los archivos HTML del proyecto."""
import os
import re
import sys

target_dir = sys.argv[1] if len(sys.argv) > 1 else '/home/arturo/certificadoya'
fixed = 0
skipped = 0
errors = 0

for root, dirs, files in os.walk(target_dir):
    # Skip .git
    if '.git' in root:
        continue
    for fname in files:
        if not fname.endswith('.html'):
            continue
        path = os.path.join(root, fname)
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as fh:
                content = fh.read()
        except Exception as e:
            print(f'ERROR reading {path}: {e}')
            errors += 1
            continue

        # Check if it has the marker
        if '/* Menú overlay móvil */' not in content:
            continue
        
        # Check if it ALREADY has the fix (display:none just before the comment)
        idx = content.find('/* Menú overlay móvil */')
        before = content[max(0, idx-30):idx].strip()
        if 'display:none' in before or '{display:none' in content[max(0, idx-100):idx]:
            skipped += 1
            continue
        
        # Add the fix: .mobile-overlay{display:none!important}\n before the comment
        new_content = content.replace(
            '/* Menú overlay móvil */',
            '.mobile-overlay{display:none!important}\n/* Menú overlay móvil */',
            1
        )
        
        try:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(new_content)
            fixed += 1
            if fixed <= 10:
                print(f'  FIXED: {path}')
        except Exception as e:
            print(f'ERROR writing {path}: {e}')
            errors += 1

print(f'\nResumen: {fixed} parcheados, {skipped} ya tenían fix, {errors} errores')
