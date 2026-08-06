#!/usr/bin/env python3
"""Rellena secciones provincias-cercanas a 6 enlaces usando mapa_cercania.json"""
import json, os, re

BASE = "/home/arturo/certificadoya"

# Cargar mapa de cercanía
with open(f"{BASE}/herramientas/mapa_cercania.json") as f:
    mapa = json.load(f)

# Obtener slugs de carpetas existentes (excluyendo coruna)
slugs_existentes = set()
for d in os.listdir(BASE):
    if d.startswith("certificado-energetico-") and os.path.isdir(f"{BASE}/{d}"):
        slug = d.replace("certificado-energetico-", "")
        if slug != "coruna":
            slugs_existentes.add(slug)

def obtener_links_cercanas(html):
    """Extrae los slugs enlazados en la sección provincias-cercanas"""
    m = re.search(r'<section class="provincias-cercanas">(.*?)</section>', html, re.DOTALL)
    if not m:
        return set()
    section = m.group(1)
    slugs = re.findall(r'href="/certificado-energetico-([a-z-]+)/"', section)
    return set(slugs)

def get_vecinos_real(slug, max_n=10):
    """Obtiene vecinos reales del slug desde mapa_cercania.json, filtrando solo existentes"""
    entry = mapa.get(slug, {})
    candidatos = []
    
    for v in entry.get("vecinas", []):
        s = v["slug"]
        if s in slugs_existentes and s != slug:
            candidatos.append(s)
    
    # Vecinos por CCAA si no hay suficientes
    if len(candidatos) < 6:
        mi_ccaa = entry.get("ccaa")
        for s in sorted(slugs_existentes):
            if s == slug or s in candidatos:
                continue
            if mapa.get(s, {}).get("ccaa") == mi_ccaa:
                candidatos.append(s)
            if len(candidatos) >= 6:
                break
    
    return candidatos[:max_n]

# Recorrer todas las provincias
modificadas = 0
stats = {}
for slug in sorted(slugs_existentes):
    dname = f"certificado-energetico-{slug}"
    path = f"{BASE}/{dname}/index.html"
    if not os.path.exists(path):
        continue
    
    with open(path) as f:
        html = f.read()
    
    if 'class="provincias-cercanas"' not in html:
        continue
    
    links_actuales = obtener_links_cercanas(html)
    n_actual = len(links_actuales)
    
    if n_actual >= 6:
        stats[slug] = n_actual
        continue
    
    # Obtener vecinos
    vecinos = get_vecinos_real(slug)
    
    # Filtrar los que ya están y que existen
    a_anadir = []
    for v in vecinos:
        if v in links_actuales:
            continue
        if v not in slugs_existentes:
            continue
        if v == slug:
            continue
        a_anadir.append(v)
        if len(links_actuales) + len(a_anadir) >= 6:
            break
    
    if not a_anadir:
        stats[slug] = n_actual
        continue
    
    # Obtener nombre para cada vecino
    nuevos_li = ""
    for v in a_anadir:
        nombre = mapa.get(v, {}).get("nombre", v.replace("-", " ").title())
        nuevos_li += f'\n                <li><a href="/certificado-energetico-{v}/">{nombre}</a></li>'
    
    # Insertar dentro de <ul> de provincias-cercanas
    html_nuevo = re.sub(
        r'(<section class="provincias-cercanas">.*?<ul>)(.*?)(</ul>)',
        lambda m: m.group(1) + m.group(2) + nuevos_li + '\n            ' + m.group(3),
        html,
        flags=re.DOTALL
    )
    
    if html_nuevo != html:
        with open(path, 'w') as f:
            f.write(html_nuevo)
        modificadas += 1
        stats[slug] = n_actual + len(a_anadir)
        print(f"  {slug}: {n_actual} → {n_actual + len(a_anadir)} (+{','.join(a_anadir)})")
    else:
        stats[slug] = n_actual

print(f"\n=== RESULTADO ===")
print(f"Modificadas: {modificadas}")
bajos = [(s, n) for s, n in stats.items() if n < 6]
print(f"Con <6 aun: {len(bajos)}")
for slug, n in sorted(bajos, key=lambda x: x[1]):
    print(f"  {slug}: {n}")
print(f"Con 6+: {sum(1 for v in stats.values() if v >= 6)}")
