#!/usr/bin/env python3
"""Regenerar sitemap.xml con todas las URLs del sitio."""
import os
from datetime import datetime

exclude = {'seguimiento.html'}
site = "https://www.certificadoya.es"

files = []
for root, dirs, names in os.walk('.'):
    if '.git' in root or 'node_modules' in root:
        continue
    for name in names:
        if name.endswith('.html') and name not in exclude:
            full = os.path.join(root, name)
            files.append(full)

files.sort()

urlset = []
urlset.append('<?xml version="1.0" encoding="UTF-8"?>')
urlset.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

for f in files:
    rel = f[2:]  # remove ./
    if rel == 'index.html':
        loc = site + '/'
    else:
        loc = site + '/' + rel
    
    depth = rel.count('/')
    if depth == 0:
        priority = '1.0' if rel == 'index.html' else '0.8'
        changefreq = 'daily'
    elif depth == 1:
        priority = '0.7'
        changefreq = 'weekly'
    elif depth == 2:
        priority = '0.6'
        changefreq = 'weekly'
    else:
        priority = '0.5'
        changefreq = 'monthly'
    
    urlset.append('  <url>')
    urlset.append(f'    <loc>{loc}</loc>')
    urlset.append(f'    <changefreq>{changefreq}</changefreq>')
    urlset.append(f'    <priority>{priority}</priority>')
    urlset.append('  </url>')

urlset.append('</urlset>')

with open('sitemap.xml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(urlset) + '\n')

# Count
total = sum(1 for line in urlset if '<loc>' in line)
print(f"Sitemap generado: {total} URLs")
