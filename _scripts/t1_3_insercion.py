#!/usr/bin/env python3
"""PASO 3 — Inserción de enlaces blog→provinciales"""
import os, re, csv
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

blog_dir = "/home/arturo/certificadoya/blog"

# URLs de destino
urls = {
    "alicante": "https://www.certificadoya.es/certificado-energetico-alicante/",
    "madrid": "https://www.certificadoya.es/precio-certificado-energetico-madrid/",
    "asturias": "https://www.certificadoya.es/certificado-energetico-asturias/",
    "valencia": "https://www.certificadoya.es/certificado-energetico-valencia/",
    "barcelona": "https://www.certificadoya.es/certificado-energetico-barcelona/",
    "bizkaia": "https://www.certificadoya.es/certificado-energetico-bizkaia/",
    "tenerife": "https://www.certificadoya.es/certificado-energetico-tenerife/",
    "murcia": "https://www.certificadoya.es/certificado-energetico-murcia/",
    "malaga": "https://www.certificadoya.es/certificado-energetico-malaga/",
    "baleares": "https://www.certificadoya.es/certificado-energetico-baleares/",
}

# Nombres para mostrar (con capitalización correcta)
nombres = {
    "alicante": "Alicante",
    "madrid": "Madrid",
    "asturias": "Asturias",
    "valencia": "Valencia",
    "barcelona": "Barcelona",
    "bizkaia": "Bizkaia",
    "tenerife": "Tenerife",
    "murcia": "Murcia",
    "malaga": "Málaga",
    "baleares": "Baleares",
}

# Banco de anchors variados para método "mencion" (variar por provincia)
anchors_mencion = {
    "alicante": [
        "certificado energético en Alicante",
        "el CEE en Alicante",
        "la certificación energética en Alicante",
    ],
    "madrid": [
        "precio del certificado energético en Madrid",
        "el costo del CEE en Madrid",
        "cuánto cuesta el certificado energético en Madrid",
    ],
    "asturias": [
        "certificado energético en Asturias",
        "el CEE en Asturias",
        "la certificación en Asturias",
    ],
    "valencia": [
        "certificado energético en Valencia",
        "el CEE en Valencia",
        "la certificación energética en Valencia",
    ],
    "barcelona": [
        "certificado energético en Barcelona",
        "el CEE en Barcelona",
        "la certificación en Barcelona",
    ],
    "bizkaia": [
        "certificado energético en Bizkaia",
        "el CEE en Bizkaia",
        "la certificación en Bizkaia",
    ],
    "tenerife": [
        "certificado energético en Tenerife",
        "el CEE en Tenerife",
        "la certificación en Tenerife",
    ],
    "murcia": [
        "certificado energético en Murcia",
        "el CEE en Murcia",
        "la certificación en Murcia",
    ],
    "malaga": [
        "certificado energético en Málaga",
        "el CEE en Málaga",
        "la certificación en Málaga",
    ],
    "baleares": [
        "certificado energético en Baleares",
        "el CEE en Baleares",
        "la certificación en Baleares",
    ],
}

anchors_bloque = {
    "alicante": "Certificado energético en Alicante",
    "madrid": "Precio del certificado energético en Madrid",
    "asturias": "Certificado energético en Asturias",
    "valencia": "Certificado energético en Valencia",
    "barcelona": "Certificado energético en Barcelona",
    "bizkaia": "Certificado energético en Bizkaia",
    "tenerife": "Certificado energético en Tenerife",
    "murcia": "Certificado energético en Murcia",
    "malaga": "Certificado energético en Málaga",
    "baleares": "Certificado energético en Baleares",
}

# Contador de uso de anchors para no repetir >3 veces
anchor_usage = {a: 0 for prov in anchors_mencion for a in anchors_mencion[prov]}

def get_anchor(provincia, metodo, usado_ya=None):
    """Obtener anchor variado, minimizando repeticiones"""
    if metodo == 'bloque':
        return anchors_bloque[provincia]
    # método mención
    pool = anchors_mencion[provincia]
    # Elegir el menos usado
    counts = [(anchor_usage[a], a) for a in pool]
    counts.sort()
    best = counts[0][1]
    anchor_usage[best] += 1
    return best

def provincia_en_texto(text, provincia):
    """Detectar si el texto menciona la provincia (caso insensible)"""
    patrones = [
        rf'\b{nombres[provincia]}\b',
        rf'\b{provincia.capitalize()}\b',
    ]
    for p in patrones:
        if re.search(p, text):
            return True
    return False

def primera_posicion_texto(soup, provincia):
    """Encontrar la primera posición del nombre de provincia en nodos de texto"""
    nombre = nombres[provincia]
    # Buscar en todo el documento, priorizando article/main
    for container_tag in ['article', 'main', 'body']:
        container = soup.find(container_tag)
        if container:
            break
    if not container:
        container = soup
    
    # Recorrer todos los nodos de texto en orden
    for text_node in container.find_all(string=True):
        if isinstance(text_node, NavigableString) and text_node.strip():
            parent = text_node.parent
            # No reemplazar dentro de etiquetas <a>, <script>, <style>, <h1>-<h6>, <nav>
            if parent and parent.name in ['a', 'script', 'style', 'nav', 'header']:
                continue
            if parent and parent.name and parent.name.startswith('h'):
                continue  # No enlazar en títulos
            
            # Buscar el nombre de la provincia en el texto
            # Patrones: "Madrid", "Alicante", "en Murcia", etc.
            pattern = rf'\b{re.escape(nombre)}\b'
            match = re.search(pattern, text_node)
            if match:
                return text_node, match.start(), match.end()
    return None, None, None

def insertar_enlace_mencion(soup, provincia):
    """Convertir primera mención de la provincia en enlace"""
    nombre = nombres[provincia]
    text_node, start, end = primera_posicion_texto(soup, provincia)
    if text_node is None:
        return False
    
    anchor_text = get_anchor(provincia, 'mencion')
    url = urls[provincia]
    
    # Partir el texto en tres partes: antes, el nombre, después
    before = text_node[:start]
    matched = text_node[start:end]
    after = text_node[end:]
    
    # Crear el enlace
    link = soup.new_tag('a', href=url)
    link.string = matched
    
    # Reemplazar el nodo de texto con los fragmentos
    new_nodes = []
    if before:
        new_nodes.append(NavigableString(before))
    new_nodes.append(link)
    if after:
        new_nodes.append(NavigableString(after))
    
    text_node.replace_with(*new_nodes)
    return True

def insertar_bloque(soup, provincia):
    """Insertar bloque aside antes del footer"""
    url = urls[provincia]
    anchor = get_anchor(provincia, 'bloque')
    
    # Buscar el footer o el final del contenido
    footer = soup.find('footer')
    
    # Crear el aside
    aside = soup.new_tag('aside', **{'class': 'enlaces-relacionados'})
    h3 = soup.new_tag('h3')
    h3.string = 'También disponible en tu zona'
    aside.append(h3)
    ul = soup.new_tag('ul')
    li = soup.new_tag('li')
    a = soup.new_tag('a', href=url)
    a.string = anchor
    li.append(a)
    ul.append(li)
    aside.append(ul)
    
    if footer:
        footer.insert_before(aside)
    else:
        # Insertar antes del cierre de </body>
        body = soup.find('body')
        if body:
            body.append(aside)
        else:
            soup.append(aside)
    return True

# Leer mapeo
mapeo = []
with open("/home/arturo/certificadoya/informes/t1.3-mapeo.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        mapeo.append((row['post'], row['destino'], row['metodo']))

# Agrupar por post
from collections import defaultdict
posts_work = defaultdict(list)
for post, dest, metodo in mapeo:
    posts_work[post].append((dest, metodo))

stats = {'modificados': 0, 'enlaces_insertados': 0, 'errores': []}

for post, trabajos in sorted(posts_work.items()):
    path = os.path.join(blog_dir, post)
    with open(path, encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    cambios = 0
    
    for destino, metodo in trabajos:
        if metodo == 'mencion':
            ok = insertar_enlace_mencion(soup, destino)
            if ok:
                cambios += 1
                stats['enlaces_insertados'] += 1
            else:
                # Fallback a bloque si no encuentra mención
                ok = insertar_bloque(soup, destino)
                if ok:
                    cambios += 1
                    stats['enlaces_insertados'] += 1
                    stats['errores'].append(f"{post}: {destino} no tenía mención, insertado como bloque")
        elif metodo == 'bloque':
            ok = insertar_bloque(soup, destino)
            if ok:
                cambios += 1
                stats['enlaces_insertados'] += 1
    
    if cambios > 0:
        # Guardar
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        stats['modificados'] += 1
        print(f"✅ {post}: {cambios} enlaces insertados")
    else:
        print(f"⚠️  {post}: sin cambios")

print(f"\n--- Resumen ---")
print(f"Posts modificados: {stats['modificados']}")
print(f"Enlaces insertados: {stats['enlaces_insertados']}")
print(f"Errores/fallbacks: {len(stats['errores'])}")
for e in stats['errores']:
    print(f"  ⚠️  {e}")

print(f"\nUso de anchors:")
for a, c in sorted(anchor_usage.items()):
    if c > 0:
        print(f"  '{a}': {c} veces")
