#!/usr/bin/env python3
"""Añadir schema JSON-LD a páginas de provincia (Service+areaServed) y blog (Article)."""
import os, re, json

def extract_h1(html):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
    if not m:
        m = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""

def extract_price(html):
    m = re.search(r'(\d+)[€]', html)
    return m.group(1) if m else "45"

def has_schema(html, stype):
    return stype in html

def add_schema_before_closing_head(html, schema_json):
    """Add schema JSON-LD before </head>."""
    schema_html = f'  <script type="application/ld+json">\n{json.dumps(schema_json, ensure_ascii=False, indent=4)}\n  </script>'
    return html.replace('</head>', f'{schema_html}\n</head>')

def clean_title(title):
    """Remove emojis and extra whitespace"""
    title = re.sub(r'[^\w\sáéíóúñÁÉÍÓÚÑ,.-:]', '', title).strip()
    title = re.sub(r'\s+', ' ', title)
    return title

# Province pages
prov_count = 0
blog_count = 0
provincia_nombres = {
    'a-coruna': ('A Coruña', 'A Coruña'),
    'alava': ('Vitoria-Gasteiz', 'Álava'),
    'albacete': ('Albacete', 'Albacete'),
    'alcala-de-henares': ('Alcalá de Henares', 'Madrid'),
    'alicante': ('Alicante', 'Alicante'),
    'almeria': ('Almería', 'Almería'),
    'asturias': ('Oviedo', 'Asturias'),
    'avila': ('Ávila', 'Ávila'),
    'badajoz': ('Badajoz', 'Badajoz'),
    'baleares': ('Palma', 'Islas Baleares'),
    'barcelona': ('Barcelona', 'Barcelona'),
    'bilbao': ('Bilbao', 'Vizcaya'),
    'burgos': ('Burgos', 'Burgos'),
    'caceres': ('Cáceres', 'Cáceres'),
    'cadiz': ('Cádiz', 'Cádiz'),
    'cantabria': ('Santander', 'Cantabria'),
    'castellon': ('Castellón', 'Castellón'),
    'ceuta': ('Ceuta', 'Ceuta'),
    'chamartin': ('Chamartín', 'Madrid'),
    'ciudad-real': ('Ciudad Real', 'Ciudad Real'),
    'cordoba': ('Córdoba', 'Córdoba'),
    'cuenca': ('Cuenca', 'Cuenca'),
    'gipuzkoa': ('San Sebastián', 'Guipúzcoa'),
    'girona': ('Girona', 'Girona'),
    'granada': ('Granada', 'Granada'),
    'guadalajara': ('Guadalajara', 'Guadalajara'),
    'huelva': ('Huelva', 'Huelva'),
    'huesca': ('Huesca', 'Huesca'),
    'jaen': ('Jaén', 'Jaén'),
    'la-rioja': ('Logroño', 'La Rioja'),
    'las-palmas': ('Las Palmas', 'Las Palmas'),
    'leon': ('León', 'León'),
    'lleida': ('Lleida', 'Lleida'),
    'lugo': ('Lugo', 'Lugo'),
    'madrid': ('Madrid', 'Madrid'),
    'malaga': ('Málaga', 'Málaga'),
    'melilla': ('Melilla', 'Melilla'),
    'murcia': ('Murcia', 'Murcia'),
    'navarra': ('Pamplona', 'Navarra'),
    'ourense': ('Ourense', 'Ourense'),
    'palencia': ('Palencia', 'Palencia'),
    'pontevedra': ('Pontevedra', 'Pontevedra'),
    'salamanca': ('Salamanca', 'Salamanca'),
    'salamanca-madrid': ('Salamanca', 'Madrid'),
    'segovia': ('Segovia', 'Segovia'),
    'sevilla': ('Sevilla', 'Sevilla'),
    'soria': ('Soria', 'Soria'),
    'tarragona': ('Tarragona', 'Tarragona'),
    'tenerife': ('Santa Cruz de Tenerife', 'Santa Cruz de Tenerife'),
    'teruel': ('Teruel', 'Teruel'),
    'toledo': ('Toledo', 'Toledo'),
    'urgente-madrid': ('Madrid', 'Madrid'),
    'valencia': ('Valencia', 'Valencia'),
    'valladolid': ('Valladolid', 'Valladolid'),
    'zamora': ('Zamora', 'Zamora'),
    'zaragoza': ('Zaragoza', 'Zaragoza'),
}

# Process province/city folders
for folder in sorted(os.listdir('.')):
    if not folder.startswith('certificado-energetico-') or not os.path.isdir(folder):
        continue
    index = os.path.join(folder, 'index.html')
    if not os.path.exists(index):
        continue
    
    with open(index, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Skip if already has Service schema
    if has_schema(html, '"Service"') or has_schema(html, '"LocalBusiness"'):
        continue
    
    # Extract city name from folder name
    city_key = folder.replace('certificado-energetico-', '')
    if city_key in provincia_nombres:
        city_name, prov_name = provincia_nombres[city_key]
    else:
        # Try from H1
        h1 = clean_title(extract_h1(html))
        city_name = h1.replace('Certificado Energético ', '').replace(' en ', '').strip()
        prov_name = city_name
    
    price = extract_price(html)
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": f"Certificado Energético en {city_name}",
        "provider": {
            "@type": "Organization",
            "name": "CertificadoYa",
            "url": "https://www.certificadoya.es/"
        },
        "areaServed": {
            "@type": "City",
            "name": city_name,
            "containedInPlace": {
                "@type": "State",
                "name": prov_name
            }
        },
        "serviceType": "Certificado de Eficiencia Energética (CEE)",
        "description": f"Emisión y registro del CEE oficial en {city_name}. Técnico colegiado, presupuesto desde {price}€.",
        "offers": {
            "@type": "Offer",
            "price": price,
            "priceCurrency": "EUR",
            "availability": "https://schema.org/InStock"
        }
    }
    
    new_html = add_schema_before_closing_head(html, schema)
    with open(index, 'w', encoding='utf-8') as f:
        f.write(new_html)
    prov_count += 1
    print(f"  ✅ {folder}: Service schema ({city_name}, {prov_name})")

# Blog posts - add Article schema
blog_dir = 'blog'
if os.path.isdir(blog_dir):
    for entry in sorted(os.listdir(blog_dir)):
        blog_path = os.path.join(blog_dir, entry)
        
        # Handle both direct .html and index.html in subfolder
        if os.path.isdir(blog_path):
            index_path = os.path.join(blog_path, 'index.html')
            if os.path.exists(index_path):
                blog_path = index_path
            else:
                continue
        elif not entry.endswith('.html') or entry == 'posts.json':
            continue
        
        with open(blog_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        if has_schema(html, '"Article"'):
            continue
        
        title = clean_title(extract_h1(html))
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "publisher": {
                "@type": "Organization",
                "name": "CertificadoYa",
                "url": "https://www.certificadoya.es/"
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"https://www.certificadoya.es/blog/{entry}"
            }
        }
        
        new_html = add_schema_before_closing_head(html, schema)
        with open(blog_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        blog_count += 1
        print(f"  ✅ blog/{entry}: Article schema ({title[:50]})")

print(f"\nResumen: {prov_count} provincias + {blog_count} blogs = {prov_count + blog_count} páginas con schema nuevo")
