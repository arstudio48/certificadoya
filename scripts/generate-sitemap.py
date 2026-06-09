#!/usr/bin/env python3
"""Generate sitemap.xml for certificadoya.es, excluding redirect pages and noindex pages."""
import os, datetime

BASE_DIR = "/home/arturo/certificadoya"
SITE = "https://www.certificadoya.es"
TODAY = datetime.date.today().isoformat()

# Exclude these root-level .html pages (they are noindex redirect pages)
EXCLUDE_HTML = [
    "a-coruna.html", "alava.html", "albacete.html", "alicante.html", "almeria.html",
    "asturias.html", "avila.html", "badajoz.html", "baleares.html", "barcelona.html",
    "bizkaia.html", "burgos.html", "caceres.html", "cadiz.html", "cantabria.html",
    "castellon.html", "ceuta.html", "ciudad-real.html", "cordoba.html", "cuenca.html",
    "gipuzkoa.html", "girona.html", "granada.html", "guadalajara.html", "huelva.html",
    "huesca.html", "jaen.html", "la-rioja.html", "las-palmas.html", "leon.html",
    "lleida.html", "lugo.html", "madrid.html", "malaga.html", "melilla.html",
    "murcia.html", "navarra.html", "ourense.html", "palencia.html", "pontevedra.html",
    "salamanca.html", "segovia.html", "sevilla.html", "soria.html", "tarragona.html",
    "tenerife.html", "teruel.html", "toledo.html", "valencia.html", "valladolid.html",
    "zamora.html", "zaragoza.html",
    # These are also redirect pages
    "index.html",  # index.html = homepage, keep it?
]

# Pages to include in sitemap (root-level .html files that are real content)
INCLUDE_ROOT_PAGES = [
    ("index.html", "weekly", 1.0),
    ("contacto.html", "monthly", 0.6),
    ("pool-encargos.html", "monthly", 0.6),
    ("panel-tecnicos.html", "monthly", 0.6),
    ("habla-con-nosotros.html", "monthly", 0.6),
    ("seguimiento.html", "monthly", 0.6),
    ("organismos-contacto.html", "monthly", 0.6),
    ("directorio-tecnicos.html", "monthly", 0.6),
    ("ver-presupuesto.html", "monthly", 0.7),
]

def get_existing_dir_pages(base_dir, prefix):
    """Get list of directory-based pages (e.g., certificado-energetico-*/)."""
    pages = []
    if not os.path.isdir(base_dir):
        return pages
    for entry in os.listdir(base_dir):
        full_path = os.path.join(base_dir, entry)
        if os.path.isdir(full_path) and entry.startswith(prefix):
            # Check it has an index.html
            if os.path.isfile(os.path.join(full_path, "index.html")):
                pages.append(entry)
    return sorted(pages)

def get_blog_posts(blog_dir):
    """Get blog HTML posts."""
    posts = []
    if not os.path.isdir(blog_dir):
        return posts
    for entry in sorted(os.listdir(blog_dir)):
        if entry.endswith(".html"):
            posts.append(f"blog/{entry}")
    return posts

def get_technician_pages(tecnicos_dir):
    """Get technician profile directories."""
    pages = []
    if not os.path.isdir(tecnicos_dir):
        return pages
    for entry in sorted(os.listdir(tecnicos_dir)):
        full_path = os.path.join(tecnicos_dir, entry)
        if os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, "index.html")):
            pages.append(f"tecnicos/{entry}/")
    return pages

def generate_sitemap():
    urls = []
    
    # 1. Root static pages
    for page, changefreq, priority in INCLUDE_ROOT_PAGES:
        file_path = os.path.join(BASE_DIR, page)
        if os.path.isfile(file_path):
            if page == "index.html":
                urls.append((f"{SITE}/", changefreq, priority))
            else:
                urls.append((f"{SITE}/{page}", changefreq, priority))
    
    # 2. Blog
    for post in get_blog_posts(os.path.join(BASE_DIR, "blog")):
        urls.append((f"{SITE}/{post}", "monthly", 0.8))
    # Blog index
    urls.append((f"{SITE}/blog/", "weekly", 0.9))
    
    # 3. Certificate pages (directories) — only real content pages (no redirects)
    for page in get_existing_dir_pages(BASE_DIR, "certificado-energetico"):
        urls.append((f"{SITE}/{page}/", "monthly", 0.7))
    
    # 4. Other directory-based pages
    other_dirs = [
        ("multa-no-tener-certificado-energetico-asturias", "monthly", 0.7),
        ("precio-certificado-energetico-madrid", "monthly", 0.7),
    ]
    for dir_name, changefreq, priority in other_dirs:
        dir_path = os.path.join(BASE_DIR, dir_name)
        if os.path.isdir(dir_path) and os.path.isfile(os.path.join(dir_path, "index.html")):
            urls.append((f"{SITE}/{dir_name}/", changefreq, priority))
    
    # 5. Technician pages
    tecnicos_index = os.path.join(BASE_DIR, "tecnicos", "index.html")
    if os.path.isfile(tecnicos_index):
        urls.append((f"{SITE}/tecnicos/", "monthly", 0.5))
    for tech_page in get_technician_pages(os.path.join(BASE_DIR, "tecnicos")):
        urls.append((f"{SITE}/{tech_page}", "monthly", 0.5))
    
    # 6. Omitimos páginas con noindex (privacidad, aviso-legal, cookies legales ya no están en el sitemap)
    
    # 7. Descargables
    for page in get_existing_dir_pages(os.path.join(BASE_DIR, "descargables"), "plantilla"):
        urls.append((f"{SITE}/descargables/{page}", "monthly", 0.7))
    # Also check if descargables has HTML files
    desc_dir = os.path.join(BASE_DIR, "descargables")
    if os.path.isdir(desc_dir):
        for f in sorted(os.listdir(desc_dir)):
            if f.endswith(".html"):
                urls.append((f"{SITE}/descargables/{f}", "monthly", 0.7))
    
    # Generate XML
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, changefreq, priority in urls:
        xml += f'  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>\n'
    xml += '</urlset>\n'
    
    output_path = os.path.join(BASE_DIR, "sitemap.xml")
    with open(output_path, 'w') as f:
        f.write(xml)
    
    print(f"Sitemap generated: {output_path}")
    print(f"Total URLs: {len(urls)}")

if __name__ == "__main__":
    generate_sitemap()
