#!/usr/bin/env python3
"""PASO 2 — Mapeo: detectar menciones de provincias y asignar destinos"""
import os, re, csv, json

blog_dir = "/home/arturo/certificadoya/blog"
posts = sorted([f for f in os.listdir(blog_dir) if f.endswith('.html') and f != 'index.html'])

# Destinos prioritarios en orden
prioritarios = [
    "alicante", "madrid", "asturias", "valencia", "barcelona",
    "bizkaia", "tenerife", "murcia", "malaga", "baleares"
]

# URL especial
urls = {
    "madrid": "/precio-certificado-energetico-madrid/",
}
for p in prioritarios:
    if p not in urls:
        urls[p] = f"/certificado-energetico-{p}/"

# Mapa de términos de búsqueda -> provincia clave
# Incluye ciudades principales que pertenecen a provincias
terminos = {
    # Alicante
    "alicante": "alicante", "alacant": "alicante", "elche": "alicante", "benidorm": "alicante",
    "torrevieja": "alicante", "alcoy": "alicante", "alcoi": "alicante", "denia": "alicante", "dénia": "alicante",
    # Madrid
    "madrid": "madrid", "alcalá": "madrid", "alcala": "madrid", "mostoles": "madrid", "móstoles": "madrid",
    "fuenlabrada": "madrid", "leganés": "madrid", "leganes": "madrid", "getafe": "madrid",
    "alcobendas": "madrid", "torrejón": "madrid", "torrejon": "madrid",
    # Asturias
    "asturias": "asturias", "oviedo": "asturias", "gijón": "asturias", "gijon": "asturias",
    "avilés": "asturias", "aviles": "asturias", "siero": "asturias",
    # Valencia
    "valencia": "valencia", "valència": "valencia", "castellón": "valencia", "castellon": "valencia",
    "torrent": "valencia", "gandía": "valencia", "gandia": "valencia", "paterna": "valencia",
    # Barcelona
    "barcelona": "barcelona", "badalona": "barcelona", "l'hospitalet": "barcelona",
    "hospitalet": "barcelona", "sabadell": "barcelona", "terrassa": "barcelona",
    "mataró": "barcelona", "mataro": "barcelona", "cornellà": "barcelona", "cornella": "barcelona",
    "lobregat": "barcelona",
    # Bizkaia
    "bizkaia": "bizkaia", "vizcaya": "bizkaia", "bilbao": "bizkaia", "bilbo": "bizkaia",
    "barakaldo": "bizkaia", "baracaldo": "bizkaia", "getxo": "bizkaia", "portugalete": "bizkaia",
    # Tenerife
    "tenerife": "tenerife", "santa cruz": "tenerife", "la laguna": "tenerife", "san cristóbal": "tenerife",
    "adeje": "tenerife", "arona": "tenerife", "puerto de la cruz": "tenerife",
    # Murcia
    "murcia": "murcia", "cartagena": "murcia", "lorca": "murcia",
    # Málaga
    "malaga": "malaga", "málaga": "malaga", "marbella": "malaga", "fuengirola": "malaga",
    "vélez": "malaga", "velez": "malaga", "torremolinos": "malaga", "estepona": "malaga",
    # Baleares
    "baleares": "baleares", "mallorca": "baleares", "menorca": "baleares", "ibiza": "baleares",
    "palma": "baleares", "cala": "baleares",
}

# Cargar contenido de cada post
mapeo = []  # list of (post, destino, metodo)

for post in posts:
    path = os.path.join(blog_dir, post)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    
    # Extraer body (entre <article> o <main> o el contenido principal)
    # Buscar contenido textual
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.IGNORECASE | re.DOTALL)
    body = body_match.group(1) if body_match else content
    
    # Quitar HTML tags para buscar texto plano
    text = re.sub(r'<[^>]+>', ' ', body)
    text_lower = text.lower()
    
    # Detectar provincias mencionadas
    mencionadas = set()
    for termino, provincia in terminos.items():
        if re.search(r'\b' + re.escape(termino) + r'\b', text_lower):
            mencionadas.add(provincia)
    
    # Asignar destinos: máximo 3 por post
    destinos_asignados = []
    
    # 1. Añadir menciones (hasta 3 del orden prioritario)
    for p in prioritarios:
        if p in mencionadas:
            destinos_asignados.append((p, 'mencion'))
            if len(destinos_asignados) >= 3:
                break
    
    # 2. Si faltan para llegar a 3, completar con bloque
    if len(destinos_asignados) < 3:
        prioridad_restantes = [p for p in prioritarios if p not in [d[0] for d in destinos_asignados]]
        for p in prioridad_restantes:
            destinos_asignados.append((p, 'bloque'))
            if len(destinos_asignados) >= 3:
                break
    
    for dest, metodo in destinos_asignados:
        mapeo.append((post, dest, metodo))

# Guardar CSV
csv_path = "/home/arturo/certificadoya/informes/t1.3-mapeo.csv"
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['post', 'destino', 'metodo'])
    for post, dest, metodo in mapeo:
        w.writerow([post, dest, metodo])

# Mostrar resumen
print(f"Mapeo generado: {len(mapeo)} asignaciones para {len(posts)} posts")
print(f"\nCSV guardado en: {csv_path}")

# Mostrar tabla
print(f"\n{'POST':<50} {'DESTINO':<15} {'MÉTODO'}")
print("-" * 80)
for post, dest, metodo in mapeo:
    print(f"{post:<50} {urls[dest]:<15} {metodo}")

# Verificar destinos existen
dest_existentes = set()
for dest, metodo_set in [(d, m) for _, d, m in mapeo]:
    ruta = urls[dest]
    dest_dir = f"/home/arturo/certificadoya{ruta.rstrip('/')}"
    if os.path.isdir(dest_dir):
        dest_existentes.add(dest)

print(f"\n--- Validación de destinos ---")
print(f"Destinos únicos asignados: {len(set(d[1] for d in mapeo))}")
for dest in sorted(set(d[1] for d in mapeo)):
    ruta = urls[dest]
    dir_path = f"/home/arturo/certificadoya{ruta.rstrip('/')}"
    existe = os.path.isdir(dir_path) and os.path.exists(os.path.join(dir_path, 'index.html'))
    print(f"  {ruta:<45} {'✅ EXISTE' if existe else '❌ NO EXISTE'}")
