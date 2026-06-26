#!/usr/bin/env python3
"""Comprime imágenes JPEG del blog de CertificadoYa para mejorar velocidad."""
import os
from PIL import Image

IMG_DIR = 'C:/Users/artur/certificadoya/img/blog'
QUALITY = 82  # Balance calidad/peso

stats = []
for fname in sorted(os.listdir(IMG_DIR)):
    if not fname.lower().endswith(('.jpg', '.jpeg')):
        continue
    fpath = os.path.join(IMG_DIR, fname)
    orig_size = os.path.getsize(fpath)
    if orig_size < 80000:  # Saltar las que ya son ligeras
        continue
    
    try:
        img = Image.open(fpath)
        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Optimizar
        tmp_path = fpath + '.tmp'
        img.save(tmp_path, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
        new_size = os.path.getsize(tmp_path)
        saving = orig_size - new_size
        pct = (saving / orig_size) * 100
        
        if saving > 0:
            os.replace(tmp_path, fpath)
            stats.append((fname, orig_size, new_size, saving, pct))
            print(f'✅ {fname}: {orig_size//1024}KB → {new_size//1024}KB (-{saving//1024}KB, {pct:.0f}%)')
        else:
            os.remove(tmp_path)
            print(f'⏭️  {fname}: ya optimizada')
    
    except Exception as e:
        print(f'❌ {fname}: {e}')

if stats:
    total_orig = sum(s[1] for s in stats)
    total_new = sum(s[2] for s in stats)
    total_save = total_orig - total_new
    print(f'\n📊 Total: {total_orig//1024}KB → {total_new//1024}KB (ahorro {total_save//1024}KB, {total_save/total_orig*100:.0f}%)')
else:
    print('\nNada que optimizar')
