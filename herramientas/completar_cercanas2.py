#!/usr/bin/env python3
"""Segundo pase: rellena las que quedan con <6 añadiendo otras de la misma CCAA"""
import json, os, re

BASE = "/home/arturo/certificadoya"

with open(f"{BASE}/herramientas/mapa_cercania.json") as f:
    mapa = json.load(f)

slugs_existentes = set()
for d in os.listdir(BASE):
    if d.startswith("certificado-energetico-") and os.path.isdir(f"{BASE}/{d}"):
        slug = d.replace("certificado-energetico-", "")
        if slug != "coruna":
            slugs_existentes.add(slug)

# Agrupar por CCAA
ccaa_slugs = {}
for s in slugs_existentes:
    ccaa = mapa.get(s, {}).get("ccaa", "")
    ccaa_slugs.setdefault(ccaa, []).append(s)

def obtener_links_cercanas(html):
    m = re.search(r'<section class="provincias-cercanas">(.*?)</section>', html, re.DOTALL)
    if not m:
        return set()
    slugs = re.findall(r'href="/certificado-energetico-([a-z-]+)/"', m.group(1))
    return set(slugs)

modificadas = 0
for slug in sorted(slugs_existentes):
    path = f"{BASE}/certificado-energetico-{slug}/index.html"
    if not os.path.exists(path):
        continue
    
    with open(path) as f:
        html = f.read()
    
    if 'class="provincias-cercanas"' not in html:
        continue
    
    links = obtener_links_cercanas(html)
    n = len(links)
    if n >= 6:
        continue
    
    # Vecinos del mapa
    entry = mapa.get(slug, {})
    mi_ccaa = entry.get("ccaa", "")
    candidatos = [v["slug"] for v in entry.get("vecinas", []) if v["slug"] in slugs_existentes and v["slug"] != slug]
    
    # Añadir otras de misma CCAA
    for s in ccaa_slugs.get(mi_ccaa, []):
        if s not in candidatos and s not in links and s != slug:
            candidatos.append(s)
    
    # Añadir cualquier provincia no enlazada como último recurso
    for s in sorted(slugs_existentes):
        if s not in candidatos and s not in links and s != slug:
            candidatos.append(s)
    
    a_anadir = []
    for v in candidatos:
        if v in links or v == slug:
            continue
        a_anadir.append(v)
        if len(links) + len(a_anadir) >= 6:
            break
    
    if not a_anadir:
        continue
    
    nuevos_li = ""
    for v in a_anadir:
        nombre = mapa.get(v, {}).get("nombre", v.replace("-", " ").title())
        nuevos_li += f'\n                <li><a href="/certificado-energetico-{v}/">{nombre}</a></li>'
    
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
        n_final = len(links) + len(a_anadir)
        print(f"  {slug}: {len(links)} → {n_final} (+{','.join(a_anadir)})")

print(f"\nModificadas segundo pase: {modificadas}")

# Verificar final
restantes = 0
for slug in sorted(slugs_existentes):
    path = f"{BASE}/certificado-energetico-{slug}/index.html"
    with open(path) as f:
        html = f.read()
    links = obtener_links_cercanas(html)
    n = len(links)
    if n < 6:
        restantes += 1
        print(f"  AUN <6: {slug}: {n}")
print(f"\nTotal con <6 tras segundo pase: {restantes}")
