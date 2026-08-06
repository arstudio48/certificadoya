#!/usr/bin/env python3
"""Actualiza el bloque de internal linking en artículos del blog.
Detecta provincias relevantes según el contenido del artículo.
Si el artículo ya tiene bloque pero con provincias genéricas, lo reemplaza por provincias relevantes."""

import os
import re
import glob
import json

PROVINCIAS = {
    "madrid": "Madrid", "barcelona": "Barcelona", "valencia": "Valencia", "sevilla": "Sevilla",
    "asturias": "Asturias", "malaga": "Málaga", "alicante": "Alicante", "zaragoza": "Zaragoza",
    "murcia": "Murcia", "granada": "Granada", "tenerife": "Tenerife", "las-palmas": "Las Palmas",
    "a-coruna": "A Coruña", "gipuzkoa": "Gipuzkoa", "bizkaia": "Bizkaia", "almeria": "Almería",
    "avila": "Ávila", "badajoz": "Badajoz", "baleares": "Baleares", "burgos": "Burgos",
    "caceres": "Cáceres", "cadiz": "Cádiz", "cantabria": "Cantabria", "castellon": "Castellón",
    "ciudad-real": "Ciudad Real", "cordoba": "Córdoba", "cuenca": "Cuenca", "girona": "Girona",
    "guadalajara": "Guadalajara", "huelva": "Huelva", "huesca": "Huesca", "jaen": "Jaén",
    "la-rioja": "La Rioja", "leon": "León", "lleida": "Lleida", "lugo": "Lugo",
    "navarra": "Navarra", "ourense": "Ourense", "palencia": "Palencia",
    "pontevedra": "Pontevedra", "salamanca": "Salamanca", "segovia": "Segovia",
    "soria": "Soria", "tarragona": "Tarragona", "teruel": "Teruel", "toledo": "Toledo",
    "valladolid": "Valladolid", "zamora": "Zamora"
}

# Mapa de keywords → provincias relevantes
TOPIC_MAP = {
    "madrid": ["madrid", "alcala", "getafe", "mostoles", "leganes"],
    "barcelona": ["barcelona", "lhospitalet", "badalona", "terrassa", "sabadell"],
    "valencia": ["valencia", "castellon", "alicante"],
    "andalucia": ["sevilla", "malaga", "granada", "cadiz", "almeria", "jaen", "huelva", "cordoba"],
    "galicia": ["a-coruna", "lugo", "ourense", "pontevedra"],
    "asturias": ["asturias"],
    "pais vasco": ["bizkaia", "gipuzkoa", "alava"],
    "catalunya": ["barcelona", "girona", "lleida", "tarragona"],
    "canarias": ["tenerife", "las-palmas"],
    "castilla y leon": ["leon", "burgos", "valladolid", "palencia", "salamanca", "segovia", "avila", "soria", "zamora"],
    "castilla-la mancha": ["toledo", "guadalajara", "ciudad-real", "cuenca", "albacete"],
    "aragon": ["zaragoza", "huesca", "teruel"],
}

def get_provincias_for_article(content, filename):
    """Detecta provincias relevantes según contenido + nombre de archivo."""
    found = []
    content_lower = content.lower()
    
    # 1. Buscar menciones directas de provincias en el contenido
    for slug, name in PROVINCIAS.items():
        if name.lower() in content_lower:
            found.append(slug)
            if len(found) >= 3:
                break
    
    # 2. Si no encontró, buscar por tópicos
    if not found:
        for topic, provs in TOPIC_MAP.items():
            if topic in content_lower:
                found.extend(provs[:3])
                break
    
    # 3. Si aún nada, TOP 5
    if not found:
        found = ["madrid", "barcelona", "valencia", "sevilla", "asturias"]
    
    return found[:5]

def detect_old_block(content):
    """Detecta si ya existe el bloque cta-tecnicos y lo devuelve para reemplazar."""
    pattern = r'<div class="cta-tecnicos"[^>]*>.*?<a href="/#presupuesto[^"]*"[^>]*>.*?</a>\s*</div>'
    matches = list(re.finditer(pattern, content, re.DOTALL))
    if matches:
        return matches[0].group()
    return None

def generate_block(prov_slugs, presupuesto_link='/#presupuesto-card'):
    """Genera el bloque HTML con enlaces personalizados."""
    links_html = '\n'.join(
        f'      <a href="/certificado-energetico-{slug}/" class="prov-link">{PROVINCIAS[slug]}</a>'
        for slug in prov_slugs
    )
    
    return f'''  <div class="cta-tecnicos" style="text-align:center">
    <h3>📋 Certificado energético en tu provincia</h3>
    <p style="margin:.5rem 0;font-size:.9rem">Presupuesto instantáneo. Técnicos verificados. Desde 45€ en 24h.</p>
    <div class="provincias-grid-v2" style="display:flex;flex-wrap:wrap;gap:.4rem;justify-content:center;margin:.75rem 0">
{links_html}
    </div>
    <a href="{presupuesto_link}" class="btn-cta" style="display:inline-block;text-decoration:none;margin-top:.5rem">Calcular mi presupuesto →</a>
  </div>'''

def main():
    blog_dir = "C:/Users/artur/certificadoya/blog"
    articles = sorted(glob.glob(os.path.join(blog_dir, "*.html")))
    articles = [a for a in articles if not a.endswith("index.html") and not a.endswith("posts.json")]
    
    modified = 0
    for article_path in articles:
        with open(article_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        filename = os.path.basename(article_path)
        prov_slugs = get_provincias_for_article(content, filename)
        
        old_block = detect_old_block(content)
        new_block = generate_block(prov_slugs)
        
        if old_block and old_block != new_block:
            new_content = content.replace(old_block, new_block, 1)
            with open(article_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ {filename} → {', '.join([PROVINCIAS[s] for s in prov_slugs])}")
            modified += 1
        elif not old_block:
            # Insertar antes de </main>
            if '</main>' in content:
                new_content = content.replace('</main>', f'{new_block}\n\n</main>', 1)
                with open(article_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"➕ {filename} → {', '.join([PROVINCIAS[s] for s in prov_slugs])} (nuevo)")
                modified += 1
    
    print(f"\n📊 {modified} artículos actualizados")

if __name__ == "__main__":
    main()
