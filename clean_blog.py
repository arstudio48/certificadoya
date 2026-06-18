#!/usr/bin/env python3
"""
Limpieza masiva de artículos del blog:
- Elimina breadcrumb duplicado dentro de .post-content
- Elimina article-header duplicado dentro de .post-content
- Cambia Outfit → DM+Sans en links de Google Fonts
- Mueve .autor-box antes del primer .blog-cta tras .article-body
- Añade BlogPosting schema si falta (usando article:published_time)
"""
import os
import re
import glob

BLOG_DIR = os.path.join(os.path.dirname(__file__), "blog")

BLOGPOSTING_TEMPLATE = """<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": {headline},
  "description": {description},
  "url": {url},
  "datePublished": "{date_published}",
  "dateModified": "{date_published}",
  "author": {{
    "@type": "Organization",
    "name": "CertificadoYa",
    "url": "https://www.certificadoya.es/"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "CertificadoYa",
    "logo": {{"@type": "ImageObject", "url": "https://www.certificadoya.es/img/og-image.png"}}
  }},
  "mainEntityOfPage": {{"@type": "WebPage", "@id": {url}}}
}}
</script>"""


def extract_meta(html: str, prop: str, attr: str = "content") -> str:
    """Extrae el valor de una etiqueta meta."""
    pattern = rf'<meta[^>]+(?:property|name)=["\'](?:og:|article:)?{re.escape(prop)}["\'][^>]+{attr}=["\']([^"\']+)["\']'
    m = re.search(pattern, html, re.IGNORECASE)
    if not m:
        pattern2 = rf'<meta[^>]+{attr}=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:|article:)?{re.escape(prop)}["\']'
        m = re.search(pattern2, html, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extract_title(html: str) -> str:
    m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def json_str(s: str) -> str:
    """Convierte una cadena Python en un literal JSON."""
    import json
    return json.dumps(s, ensure_ascii=False)


def remove_duplicate_breadcrumb(html: str) -> str:
    """Elimina <nav class="breadcrumb">...</nav> dentro de .post-content"""
    # Patrón: dentro de post-content, eliminar nav.breadcrumb (puede estar comentado con <!-- Breadcrumb -->)
    # Eliminamos el comentario + el nav
    html = re.sub(
        r"<!-- Breadcrumb -->\s*\n?\s*<nav[^>]+class=[\"'][^\"']*breadcrumb[^\"']*[\"'][^>]*>.*?</nav>",
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # También sin comentario
    html = re.sub(
        r"<nav[^>]+class=[\"'][^\"']*breadcrumb[^\"'][^>]*aria-label=[\"']Breadcrumb[\"'][^>]*>.*?</nav>",
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    html = re.sub(
        r"<nav[^>]+aria-label=[\"']Breadcrumb[\"'][^>]+class=[\"'][^\"']*breadcrumb[^\"']*[\"'][^>]*>.*?</nav>",
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return html


def remove_duplicate_article_header(html: str) -> str:
    """Elimina <header class="article-header">...</header> dentro de .post-content"""
    html = re.sub(
        r"<!-- Header -->\s*\n?\s*<header[^>]+class=[\"'][^\"']*article-header[^\"']*[\"'][^>]*>.*?</header>",
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    html = re.sub(
        r"<header[^>]+class=[\"'][^\"']*article-header[^\"']*[\"'][^>]*>.*?</header>",
        "",
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return html


def fix_google_fonts(html: str) -> str:
    """Cambia Outfit por DM+Sans en el link de Google Fonts."""
    html = re.sub(
        r"family=Outfit:[^\"'&]+",
        "family=DM+Sans:wght@300;400;500;600;700",
        html,
    )
    html = re.sub(
        r"family=Outfit%3A[^\"'&]+",
        "family=DM+Sans:wght@300;400;500;600;700",
        html,
    )
    return html


def move_autor_box(html: str) -> str:
    """Mueve .autor-box antes del primer .blog-cta que sigue a .article-body."""
    # Extraemos el autor-box (con su style inline si lo lleva)
    autor_match = re.search(
        r'<div class="autor-box">.*?</div>(?:\s*<style>.*?</style>)?',
        html,
        flags=re.DOTALL,
    )
    if not autor_match:
        return html

    autor_block = autor_match.group(0)
    # Eliminamos el bloque del autor de su posición actual
    html_sin_autor = html[: autor_match.start()] + html[autor_match.end() :]

    # Buscamos el primer .blog-cta tras .article-body
    cta_match = re.search(r'<div class="blog-cta">', html_sin_autor)
    if not cta_match:
        return html  # Si no hay CTA, no movemos

    insert_pos = cta_match.start()
    html_nuevo = (
        html_sin_autor[:insert_pos]
        + autor_block
        + "\n"
        + html_sin_autor[insert_pos:]
    )
    return html_nuevo


def has_blogposting_schema(html: str) -> bool:
    return '"BlogPosting"' in html


def add_blogposting_schema(html: str, filepath: str) -> str:
    """Añade BlogPosting schema antes del cierre de </head>."""
    date_published = extract_meta(html, "published_time")
    if not date_published:
        date_published = "2026-01-01"

    og_title = extract_meta(html, "title")
    if not og_title:
        og_title = extract_title(html)

    og_description = extract_meta(html, "description")
    og_url = extract_meta(html, "url")

    schema = BLOGPOSTING_TEMPLATE.format(
        headline=json_str(og_title),
        description=json_str(og_description),
        url=json_str(og_url),
        date_published=date_published,
    )

    html = re.sub(r"</head>", schema + "\n</head>", html, count=1, flags=re.IGNORECASE)
    return html


def process_file(filepath: str) -> tuple[bool, list[str]]:
    """Procesa un archivo HTML. Devuelve (modificado, lista_cambios)."""
    with open(filepath, encoding="utf-8") as f:
        original = f.read()

    html = original
    changes = []

    # 1. Eliminar breadcrumb duplicado
    html2 = remove_duplicate_breadcrumb(html)
    if html2 != html:
        changes.append("breadcrumb duplicado eliminado")
        html = html2

    # 2. Eliminar article-header duplicado
    html2 = remove_duplicate_article_header(html)
    if html2 != html:
        changes.append("article-header duplicado eliminado")
        html = html2

    # 3. Cambiar Outfit → DM+Sans
    html2 = fix_google_fonts(html)
    if html2 != html:
        changes.append("Outfit → DM+Sans")
        html = html2

    # 4. Mover autor-box antes del primer CTA
    html2 = move_autor_box(html)
    if html2 != html:
        changes.append("autor-box movido antes del CTA")
        html = html2

    # 5. Añadir BlogPosting schema si falta
    if not has_blogposting_schema(html):
        html2 = add_blogposting_schema(html, filepath)
        if html2 != html:
            changes.append("BlogPosting schema añadido")
            html = html2

    if html != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return True, changes

    return False, []


def main():
    pattern = os.path.join(BLOG_DIR, "*.html")
    files = sorted(glob.glob(pattern))
    # Excluir index.html
    files = [f for f in files if os.path.basename(f) != "index.html"]

    print(f"Procesando {len(files)} artículos en {BLOG_DIR}...")
    total_changed = 0

    for filepath in files:
        name = os.path.basename(filepath)
        modified, changes = process_file(filepath)
        if modified:
            total_changed += 1
            print(f"  ✓ {name}: {', '.join(changes)}")
        else:
            print(f"  — {name}: sin cambios")

    print(f"\nResumen: {total_changed}/{len(files)} archivos modificados.")


if __name__ == "__main__":
    main()
