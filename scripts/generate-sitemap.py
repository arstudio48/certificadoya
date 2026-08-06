#!/usr/bin/env python3
"""Generate sitemap.xml for certificadoya.es with accurate <lastmod> per URL.

Each URL gets its <lastmod> from the last git commit that touched that file,
giving Google a precise freshness signal per page. Falls back to filesystem
mtime when git is unavailable.

Usage:
    cd /c/Users/artur/certificadoya && python scripts/generate-sitemap.py
    → overwrites sitemap.xml in project root
"""
import os
import datetime
import subprocess
import sys

BASE_DIR = r"C:\Users\artur\certificadoya"
SITE = "https://www.certificadoya.es"
TODAY = datetime.date.today().isoformat()  # fallback global

# ── Exclusiones ──────────────────────────────────────────────────────────────
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
    "index.html",
]

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

# ── Git-based lastmod ────────────────────────────────────────────────────────

def git_lastmod(rel_path):
    """Return YYYY-MM-DD of the last commit that touched rel_path, or ''."""
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", rel_path],
            capture_output=True, text=True,
            cwd=BASE_DIR, timeout=10
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()[:10]  # "2026-07-27"
    except Exception:
        pass
    return file_mtime(rel_path)

def file_mtime(rel_path):
    """Fallback: filesystem mtime as YYYY-MM-DD, or ''."""
    full = os.path.join(BASE_DIR, rel_path)
    try:
        if os.path.isfile(full):
            return datetime.datetime.fromtimestamp(
                os.path.getmtime(full)
            ).strftime('%Y-%m-%d')
    except Exception:
        pass
    return TODAY  # ultimate fallback


# ── Discovery helpers ────────────────────────────────────────────────────────

def get_existing_dir_pages(base_dir, prefix):
    pages = []
    if not os.path.isdir(base_dir):
        return pages
    for entry in sorted(os.listdir(base_dir)):
        full_path = os.path.join(base_dir, entry)
        if os.path.isdir(full_path) and entry.startswith(prefix):
            if os.path.isfile(os.path.join(full_path, "index.html")):
                pages.append(entry)
    return pages

def get_blog_posts(blog_dir):
    posts = []
    if not os.path.isdir(blog_dir):
        return posts
    for entry in sorted(os.listdir(blog_dir)):
        if entry.endswith(".html"):
            posts.append(f"blog/{entry}")
    return posts

def get_technician_pages(tecnicos_dir):
    pages = []
    if not os.path.isdir(tecnicos_dir):
        return pages
    for entry in sorted(os.listdir(tecnicos_dir)):
        full_path = os.path.join(tecnicos_dir, entry)
        if os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, "index.html")):
            pages.append(f"tecnicos/{entry}/")
    return pages


# ── Generator ────────────────────────────────────────────────────────────────

def generate_sitemap():
    entries = []  # (loc, changefreq, priority, lastmod)

    # 1. Root static pages
    for page, changefreq, priority in INCLUDE_ROOT_PAGES:
        file_path = os.path.join(BASE_DIR, page)
        if os.path.isfile(file_path):
            loc = f"{SITE}/" if page == "index.html" else f"{SITE}/{page}"
            lm = git_lastmod(page)
            entries.append((loc, changefreq, priority, lm))

    # 2. Blog articles
    for post in get_blog_posts(os.path.join(BASE_DIR, "blog")):
        lm = git_lastmod(post)
        entries.append((f"{SITE}/{post}", "monthly", 0.8, lm))
    # Blog index
    lm = git_lastmod("blog/index.html")
    entries.append((f"{SITE}/blog/", "weekly", 0.9, lm))

    # 3. Certificado energético landings (directories)
    for page in get_existing_dir_pages(BASE_DIR, "certificado-energetico"):
        rel = f"{page}/index.html"
        lm = git_lastmod(rel) or file_mtime(rel)
        entries.append((f"{SITE}/{page}/", "monthly", 0.7, lm))

    # 4. Other directory-based pages
    other_dirs = [
        ("multa-no-tener-certificado-energetico-asturias", "monthly", 0.7),
        ("precio-certificado-energetico-madrid", "monthly", 0.7),
    ]
    for dir_name, changefreq, priority in other_dirs:
        rel = f"{dir_name}/index.html"
        full = os.path.join(BASE_DIR, rel)
        if os.path.isfile(full):
            lm = git_lastmod(rel)
            entries.append((f"{SITE}/{dir_name}/", changefreq, priority, lm))

    # 5. Technician pages
    if os.path.isfile(os.path.join(BASE_DIR, "tecnicos", "index.html")):
        entries.append((f"{SITE}/tecnicos/", "monthly", 0.5, git_lastmod("tecnicos/index.html")))
    for tech_page in get_technician_pages(os.path.join(BASE_DIR, "tecnicos")):
        rel = f"{tech_page}index.html"
        lm = git_lastmod(rel) or file_mtime(rel)
        entries.append((f"{SITE}/{tech_page}", "monthly", 0.5, lm))

    # 6. Descargables (directories)
    for page in get_existing_dir_pages(os.path.join(BASE_DIR, "descargables"), "plantilla"):
        rel = f"descargables/{page}/index.html"
        lm = git_lastmod(rel) or file_mtime(rel)
        entries.append((f"{SITE}/descargables/{page}/", "monthly", 0.7, lm))
    desc_dir = os.path.join(BASE_DIR, "descargables")
    if os.path.isdir(desc_dir):
        for f in sorted(os.listdir(desc_dir)):
            if f.endswith(".html"):
                rel = f"descargables/{f}"
                lm = git_lastmod(rel) or file_mtime(rel)
                entries.append((f"{SITE}/descargables/{f}", "monthly", 0.7, lm))

    # ── Generate XML ─────────────────────────────────────────────────────────
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, changefreq, priority, lastmod in entries:
        lastmod_str = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        xml += (
            f'  <url>'
            f'<loc>{loc}</loc>'
            f'{lastmod_str}'
            f'<changefreq>{changefreq}</changefreq>'
            f'<priority>{priority}</priority>'
            f'</url>\n'
        )
    xml += '</urlset>\n'

    output_path = os.path.join(BASE_DIR, "sitemap.xml")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml)

    # Stats
    with_lastmod = sum(1 for e in entries if e[3])
    without = len(entries) - with_lastmod
    print(f"Sitemap: {output_path}")
    print(f"Total URLs: {len(entries)}")
    print(f"  con <lastmod>: {with_lastmod}")
    print(f"  sin <lastmod>: {without}")
    print(f"  Último push: {git_lastmod('sitemap.xml')}")
    print("✅ Regenerado. Haz git add sitemap.xml && git commit && git push")


if __name__ == "__main__":
    generate_sitemap()
