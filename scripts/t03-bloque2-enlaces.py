#!/usr/bin/env python3
"""
T0.3 — Bloque 2: Enlaces rotos.
- Home: solo Madrid con enlace, resto sin href + atenuado + "Próximamente"
- Página Madrid: distritos (14) + provincias (8) → mismo tratamiento
- Añadir CSS para .prov-link-disabled en home
- Además: corregir "Desde 45 €" residual en index.html
"""

import os
import re

BASE = '/home/arturo/certificadoya'

def add_disabled_css(content):
    """Añade CSS para .prov-link-disabled si no existe"""
    if '.prov-link-disabled' in content:
        return content, 0
    
    css = '''
.prov-link-disabled {
    display:inline-flex;align-items:center;padding:.55rem 1.1rem;
    background:#f3f3f3;border-radius:25px;color:#999;font-size:.9rem;font-weight:500;
    cursor:default;text-decoration:none;gap:.35rem;justify-content:center
}
.prov-link-disabled small {
    font-size:.65rem;color:#bbb;font-weight:400
}'''
    
    # Insertar después de provincias-grid-v2 o en el último style block
    content, n = re.subn(r'(</style>)', css + r'\1', content, count=1)
    return content, n

def fix_home_provincias(content):
    """Transforma chips de provincia en index.html"""
    def replace_chip(m):
        slug = m.group(1)
        name = m.group(2)
        
        if slug == 'madrid':
            return f'<a href="/certificado-energetico-madrid/" class="prov-link prov-link-destacada">Madrid</a>'
        else:
            return f'<span class="prov-link prov-link-disabled">{name} <small>Próximamente</small></span>'
    
    content, n = re.subn(
        r'<a href="/certificado-energetico-([^/]+)/"\s*class="prov-link[^"]*">([^<]+)</a>',
        replace_chip,
        content
    )
    
    return content, n

def fix_madrid_page(content):
    """Corrige TODOS los enlaces rotos en la página de Madrid"""
    changes = 0
    
    # Provincias en "Otras provincias" (líneas 581-588): /XXX.html, excluir CTAs
    def replace_otra_prov(m):
        name = m.group(1)
        return f'<span style="display:inline-block;padding:.4rem .8rem;background:#f3f3f3;border:1px solid #e0e0e0;border-radius:6px;color:#999;font-size:.85rem;cursor:default">{name} <small style="font-size:.65rem;color:#bbb;font-weight:400">Próximamente</small></span>'
    
    content, n2 = re.subn(
        r'<a href="/(?:barcelona|valencia|sevilla|alicante|malaga|asturias|murcia|zaragoza)\.html"[^>]*style="[^"]*"[^>]*>([^<]+)</a>',
        replace_otra_prov,
        content
    )
    changes += n2
    if n2:
        print(f"  otras-provincias: {n2}")
    
    return content, changes

def fix_desde_45(content):
    """Corrige 'Desde 45 €' residual (con mayúscula)"""
    content, n = re.subn(r'Desde\s+45(\s*€)', r'Desde 60\g<1>', content)
    return content, n

def main():
    total = {}
    
    # 1. index.html
    path = os.path.join(BASE, 'index.html')
    with open(path, 'r') as f:
        content = f.read()
    original = content
    
    content, n0 = add_disabled_css(content)
    content, n1 = fix_home_provincias(content)
    content, n2 = fix_desde_45(content)
    
    if content != original:
        total['index.html'] = {'css': n0, 'chips': n1, 'desde45': n2}
        with open(path, 'w') as f:
            f.write(content)
        print(f"✓ index.html: css={n0}, chips={n1}, desde45={n2}")
    
    # 2. Página Madrid
    path = os.path.join(BASE, 'certificado-energetico-madrid', 'index.html')
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        original = content
        content, n = fix_madrid_page(content)
        if content != original:
            total['certificado-energetico-madrid/index.html'] = {'enlaces': n}
            with open(path, 'w') as f:
                f.write(content)
            print(f"✓ certificado-energetico-madrid/index.html: enlaces={n}")
    
    print(f"\n✅ {len(total)} archivos modificados")

if __name__ == '__main__':
    main()
