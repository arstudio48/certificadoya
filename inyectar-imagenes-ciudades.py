#!/usr/bin/env python3
"""Inyecta ilustraciones de ciudades en las landing pages de certificadoya.es"""

import re
import os

CIUDADES = [
    ("barcelona", "Barcelona", "en Barcelona capital y área metropolitana"),
    ("valencia", "Valencia", "en Valencia capital y provincia"),
    ("castellon", "Castellón", "en Castellón de la Plana y provincia"),
    ("sevilla", "Sevilla", "en Sevilla capital y provincia"),
    ("cadiz", "Cádiz", "en Cádiz capital y la provincia"),
    ("bilbao", "Bilbao", "en Bilbao y toda Vizcaya"),
]

def modificar_landing(ciudad_slug, ciudad_nombre, ambito_texto):
    slug_img = ciudad_slug  # nombre del archivo de imagen
    if ciudad_slug == "castellon":
        slug_img = "castellon"
    elif ciudad_slug == "bilbao":
        slug_img = "bilbao"
    
    ruta = f"/home/arturo/certificadoya/certificado-energetico-{ciudad_slug}/index.html"
    if not os.path.exists(ruta):
        print(f"  ❌ NO EXISTE: {ruta}")
        return False
    
    with open(ruta, 'r') as f:
        html = f.read()
    
    original_len = len(html)
    
    # 1. Añadir CSS hero-split DESPUÉS de .hero-local .lead
    css_hero_split = """
    .hero-split { display:flex; gap:2rem; align-items:center; max-width:900px; margin:0 auto 3rem; }
    .hero-split .hero-img { flex:0 0 280px; border-radius:var(--radius); overflow:hidden; box-shadow:var(--shadow); }
    .hero-split .hero-img img { width:100%; height:auto; display:block; }
    .hero-split .presupuesto-card { flex:1; max-width:100%; margin:0; }
    @media (max-width:700px) { .hero-split { flex-direction:column; } .hero-split .hero-img { flex:0 0 auto; max-width:200px; } }"""
    
    old_css_line = "    .hero-local .lead { font-size:1.1rem; color:var(--gray-600); margin-bottom:1.5rem; }"
    new_css_block = old_css_line + css_hero_split
    html = html.replace(old_css_line, new_css_block)
    
    # 2. Reemplazar el hero section y mover presupuesto-card dentro
    # Buscar: <section class="hero-local"> ... </section>  <div class="presupuesto-card" id="presupuesto-card"> ... </div>
    
    # Patrón para encontrar el hero section
    hero_pattern = re.compile(
        r'<section class="hero-local">\s*'
        r'<h1>(.*?)<span>en ' + re.escape(ciudad_nombre) + r'</span>(.*?)</h1>\s*'
        r'<p class="lead">(.*?)</p>\s*'
        r'</section>',
        re.DOTALL
    )
    
    hero_match = hero_pattern.search(html)
    if not hero_match:
        print(f"  ⚠️ No se encontró hero section para {ciudad_nombre}, intentando patrón alternativo...")
        # Patrón alternativo (sin <section>)
        hero_pattern2 = re.compile(
            r'<section class="hero-local">\s*'
            r'<h1>(.*?)<span>en(.*?)</span>(.*?)</h1>\s*'
            r'<p class="lead">(.*?)</p>\s*'
            r'</section>',
            re.DOTALL
        )
        hero_match = hero_pattern2.search(html)
        if not hero_match:
            print(f"  ❌ No se pudo encontrar hero para {ciudad_nombre}")
            return False
    
    # Extraer el h1 completo y lead
    full_h1 = hero_match.group(0).split('<h1>')[1].split('</h1>')[0]
    full_lead = hero_match.group(0).split('<p class="lead">')[1].split('</p>')[0]
    
    hero_original = hero_match.group(0)
    
    # Nuevo hero con imagen
    nuevo_hero = f'''  <div class="hero-local">
    <h1>🏠 Certificado Energético <span>en {ciudad_nombre}</span></h1>
    <p class="lead">Presupuesto online gratuito. Técnicos colegiados {ambito_texto}. Resultado oficial en 48h.</p>
    <div class="hero-split">
      <div class="hero-img">
        <img src="/images/ciudades/{slug_img}.jpg" alt="Ilustración {ciudad_nombre}" width="800" height="1134" loading="lazy">
      </div>'''
    
    html = html.replace(hero_original, nuevo_hero)
    
    # 3. Encontrar el presupuesto-card después y moverlo dentro
    # Buscar el primer presupuesto-card después del nuevo hero
    presupuesto_pattern = re.compile(
        r'<div class="presupuesto-card" id="presupuesto-card">(.*?)</div>\s*',
        re.DOTALL
    )
    
    # Buscar después de la posición del nuevo hero
    hero_end_pos = html.find(nuevo_hero) + len(nuevo_hero)
    resto = html[hero_end_pos:]
    
    presupuesto_match = presupuesto_pattern.search(resto)
    if not presupuesto_match:
        print(f"  ❌ No se encontró presupuesto-card para {ciudad_nombre}")
        return False
    
    presupuesto_html = presupuesto_match.group(0)
    
    # Extraer todo el contenido del presupuesto-card hasta el siguiente </div> que lo cierra
    # Buscar el cierre real del presupuesto-card (podría contener divs anidados)
    
    # Mejor enfoque: reemplazar el presupuesto-card original con solo el contenido
    # y añadirlo al nuevo hero
    
    # Contenido del presupuesto-card (sin el div contenedor)
    contenido_presupuesto = presupuesto_html.replace(
        '<div class="presupuesto-card" id="presupuesto-card">', ''
    )
    # Quitar el </div> de cierre del final
    if contenido_presupuesto.endswith('</div>\n'):
        contenido_presupuesto = contenido_presupuesto[:-len('</div>\n')]
    elif contenido_presupuesto.endswith('</div>'):
        contenido_presupuesto = contenido_presupuesto[:-len('</div>')]
    
    # El contenido_presupuesto incluye el formulario completo
    # Pero el cierre </div> del presupuesto-card puede ser el primer </div> después de #resultado-solicitud
    
    # Encontrar el cierre real. El presupuesto-card contiene: h3, p.subtitle, form-group, form-row, button, resultado-box, resultado-solicitud
    # Luego un </div> que cierra el card
    
    # Buscamos manualmente
    card_start = resto.find('<div class="presupuesto-card" id="presupuesto-card">')
    content_start = card_start + len('<div class="presupuesto-card" id="presupuesto-card">')
    
    # El card contiene varios divs anidados. El último </div> que lo cierra es el que está después de #resultado-solicitud
    # Buscamos #resultado-solicitud y luego el siguiente </div>
    
    sol_pos = resto.find('<div id="resultado-solicitud">', content_start)
    if sol_pos < 0:
        sol_pos = resto.find('id="resultado-solicitud"', content_start)
    
    # Buscar cierre después de resultado-solicitud
    close_start = resto.find('</div>', sol_pos + 30 if sol_pos > 0 else card_start + 200)
    # El cierre del presupuesto-card es este </div>
    if close_start > 0:
        # todo el bloque presupuesto hasta su cierre
        presupuesto_block = resto[card_start:close_start + 6]  # +6 for </div>
        
        # Extraer solo el interior
        inner_start = card_start + len('<div class="presupuesto-card" id="presupuesto-card">')
        inner_content = resto[inner_start:close_start]
        
        # Reemplazar el presupuesto-card original por el interior dentro del hero
        html = html.replace(presupuesto_block, '')
        
        # Añadir el contenido del presupuesto-card dentro del hero-split
        cierre_card = '      </div>\n    </div>\n  </div>\n'
        nuevo_hero_completo = nuevo_hero + '\n' + inner_content.strip() + '\n' + cierre_card
        
        html = html.replace(nuevo_hero, nuevo_hero_completo)
    
    # Verificar que el HTML es válido (misma longitud aprox)
    cambio = len(html) - original_len
    print(f"  ✅ {ciudad_nombre}: {cambio:+d} chars")
    
    with open(ruta, 'w') as f:
        f.write(html)
    
    return True

def modificar_cantabria():
    """Santander -> landing de Cantabria"""
    ruta = "/home/arturo/certificadoya/certificado-energetico-cantabria/index.html"
    if not os.path.exists(ruta):
        print(f"  ❌ NO EXISTE: {ruta}")
        return False
    
    with open(ruta, 'r') as f:
        html = f.read()
    
    original_len = len(html)
    ciudad_nombre = "Cantabria"
    
    # CSS
    css_hero_split = """
    .hero-split { display:flex; gap:2rem; align-items:center; max-width:900px; margin:0 auto 3rem; }
    .hero-split .hero-img { flex:0 0 280px; border-radius:var(--radius); overflow:hidden; box-shadow:var(--shadow); }
    .hero-split .hero-img img { width:100%; height:auto; display:block; }
    .hero-split .presupuesto-card { flex:1; max-width:100%; margin:0; }
    @media (max-width:700px) { .hero-split { flex-direction:column; } .hero-split .hero-img { flex:0 0 auto; max-width:200px; } }"""
    
    old_css = "    .hero-local .lead { font-size:1.1rem; color:var(--gray-600); margin-bottom:1.5rem; }"
    html = html.replace(old_css, old_css + css_hero_split)
    
    # Buscar hero section
    hero_match = re.search(r'<section class="hero-local">(.*?)</section>', html, re.DOTALL)
    if not hero_match:
        print(f"  ❌ No se encontró hero en Cantabria")
        return False
    
    hero_original = hero_match.group(0)
    nuevo_hero = '''  <div class="hero-local">
    <h1>🏠 Certificado Energético <span>en Cantabria</span></h1>
    <p class="lead">Presupuesto online gratuito. Técnicos colegiados en Santander y toda Cantabria. Resultado oficial en 48h.</p>
    <div class="hero-split">
      <div class="hero-img">
        <img src="/images/ciudades/santander.jpg" alt="Ilustración Santander" width="800" height="1134" loading="lazy">
      </div>'''
    
    html = html.replace(hero_original, nuevo_hero)
    
    # Mover presupuesto-card dentro
    resto = html[html.find(nuevo_hero) + len(nuevo_hero):]
    card_start = resto.find('<div class="presupuesto-card" id="presupuesto-card">')
    if card_start < 0:
        print(f"  ❌ No se encontró presupuesto-card en Cantabria")
        return False
    
    content_start = card_start + len('<div class="presupuesto-card" id="presupuesto-card">')
    
    # Buscar cierre
    sol_pos = resto.find('<div id="resultado-solicitud">', content_start)
    close_start = resto.find('</div>', sol_pos + 30 if sol_pos > 0 else card_start + 200)
    
    if close_start > 0:
        presupuesto_block = resto[card_start:close_start + 6]
        inner = resto[content_start:close_start]
        
        html = html.replace(presupuesto_block, '')
        
        cierre = '      </div>\n    </div>\n  </div>\n'
        html = html.replace(nuevo_hero, nuevo_hero + '\n' + inner.strip() + '\n' + cierre)
    
    cambio = len(html) - original_len
    print(f"  ✅ Cantabria (Santander): {cambio:+d} chars")
    
    with open(ruta, 'w') as f:
        f.write(html)
    return True


if __name__ == '__main__':
    print("🔧 Inyectando ilustraciones de ciudades en landing pages...\n")
    
    resultados = []
    for slug, nombre, ambito in CIUDADES:
        ok = modificar_landing(slug, nombre, ambito)
        resultados.append((nombre, "✅" if ok else "❌"))
    
    modificar_cantabria()
    resultados.append(("Cantabria", "✅"))
    
    print(f"\n📊 Resumen:")
    for nombre, estado in resultados:
        print(f"  {estado} {nombre}")
    print("\n✅ Hecho")
