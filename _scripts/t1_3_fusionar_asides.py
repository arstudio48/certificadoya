#!/usr/bin/env python3
"""Post-procesamiento: fusionar bloques aside consecutivos en uno solo"""
import os, re

blog_dir = "/home/arturo/certificadoya/blog"
posts = sorted([f for f in os.listdir(blog_dir) if f.endswith('.html') and f != 'index.html'])

fusionados = 0

for post in posts:
    path = os.path.join(blog_dir, post)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    
    # Buscar asides consecutivos (separados solo por espacios/newlines)
    # Patrón: </aside>\\s*<aside ...> → fusionar
    original = content
    
    # Mientras haya asides consecutivos
    while re.search(r'</aside>\s*<aside class="enlaces-relacionados">', content, re.DOTALL):
        # Encontrar el primer par de asides consecutivos
        m = re.search(
            r'(<aside class="enlaces-relacionados">.*?</aside>)\s*'
            r'(<aside class="enlaces-relacionados">.*?</aside>)',
            content, re.DOTALL
        )
        if not m:
            break
        
        aside1 = m.group(1)
        aside2 = m.group(2)
        
        # Extraer los <li> del segundo aside
        lis2 = re.findall(r'<li>(.*?)</li>', aside2, re.DOTALL)
        
        # Insertarlos en el primer aside, antes del </aside>
        # Pero necesito que el h3 no se duplique. El primer aside ya tiene <h3>.
        # Voy a tomar solo los <li> del segundo y añadirlos al <ul> del primero
        
        # Encontrar el <ul> del primer aside
        ul_m = re.search(r'(<ul>)(.*?)(</ul>)', aside1, re.DOTALL)
        if ul_m:
            # Añadir los li del segundo aside al ul del primero
            new_aside1 = aside1[:ul_m.start(3)] + '\n'.join(f'    <li>{l}</li>' for l in lis2) + '\n  ' + aside1[ul_m.start(3):]
            
            # Reemplazar ambos asides con el fusionado
            content = content[:m.start()] + new_aside1 + content[m.end():]
        else:
            break
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        fusionados += 1
        print(f"✅ {post}: asides fusionados")

print(f"\nTotal posts con asides fusionados: {fusionados}")
