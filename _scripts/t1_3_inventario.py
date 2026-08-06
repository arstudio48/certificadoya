#!/usr/bin/env python3
"""PASO 1 — Inventario de posts del blog y enlaces a provinciales"""
import os, re, sys

blog_dir = "/home/arturo/certificadoya/blog"
posts = sorted([f for f in os.listdir(blog_dir) if f.endswith('.html') and f != 'index.html'])

report_lines = []
total_links = 0
posts_with = 0

for post in posts:
    path = os.path.join(blog_dir, post)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    
    # Título
    m = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    title = m.group(1).strip() if m else 'SIN TÍTULO'
    
    # Enlaces a provinciales
    links = re.findall(r'href="https?://(?:www\.)?certificadoya\.es/certificado-energetico-([^/"]+)/"', content, re.IGNORECASE)
    provincias = sorted(set(links))
    n = len(provincias)
    total_links += n
    if n > 0:
        posts_with += 1
    
    report_lines.append(f"blog/{post} | {title} | enlaces: {n} | {', '.join(provincias) if provincias else 'ninguna'}")

# Output
out = []
out.append("=" * 80)
out.append("INVENTARIO T1.3 — Enlaces actuales a provinciales en blog")
out.append(f"Fecha: 2026-06-11")
out.append(f"Total posts: {len(posts)}")
out.append("-" * 80)
out.append("RUTA | TÍTULO | ENLACES ACTUALES | PROVINCIAS")
out.append("-" * 80)
out.extend(report_lines)
out.append("-" * 80)
out.append(f"Resumen: {posts_with}/{len(posts)} posts ya tienen enlaces. Total enlaces a provinciales: {total_links}.")
out.append("=" * 80)

result = "\n".join(out)
report_path = "/home/arturo/certificadoya/informes/t1.3-inventario.txt"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(result)

print(result)
