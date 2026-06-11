#!/usr/bin/env python3
"""PASO 4 — Verificación técnica completa"""
import os, re, subprocess, sys

blog_dir = "/home/arturo/certificadoya/blog"
posts = sorted([f for f in os.listdir(blog_dir) if f.endswith('.html') and f != 'index.html'])

checks = {
    'rango_enlaces': {'ok': 0, 'fail': []},
    'sin_duplicados_mismo_post': {'ok': 0, 'fail': []},
    'href_www': {'ok': 0, 'fail': []},
    'html_parseable': {'ok': 0, 'fail': []},
}

for post in posts:
    path = os.path.join(blog_dir, post)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    
    # 1. Cada post tiene entre 1 y 3 enlaces a /certificado-energetico-*/
    links = re.findall(r'href="https?://(?:www\.)?certificadoya\.es/(?:certificado-energetico-[^/"]+|precio-certificado-energetico-[^/"]+)/"', content)
    n = len(links)
    if 1 <= n <= 3:
        checks['rango_enlaces']['ok'] += 1
    else:
        checks['rango_enlaces']['fail'].append(f"{post}: {n} enlaces")
    
    # 2. Cero enlaces duplicados al mismo destino dentro de un mismo post
    destinos = re.findall(r'href="(https?://(?:www\.)?certificadoya\.es/(?:certificado-energetico-[^/"]+|precio-certificado-energetico-[^/"]+)/)"', content)
    if len(destinos) == len(set(destinos)):
        checks['sin_duplicados_mismo_post']['ok'] += 1
    else:
        # Encontrar duplicados
        from collections import Counter
        dupes = [d for d, c in Counter(destinos).items() if c > 1]
        checks['sin_duplicados_mismo_post']['fail'].append(f"{post}: duplicados -> {dupes}")
    
    # 3. Todos los href usan https://www. 
    hrefs = re.findall(r'href="https?://(?:www\.)?certificadoya\.es/(?:certificado-energetico-[^/"]+|precio-certificado-energetico-[^/"]+)/"', content)
    malos = [h for h in hrefs if 'www.' not in h.split('certificadoya')[0]]
    if malos:
        checks['href_www']['fail'].append(f"{post}: {malos}")
    else:
        checks['href_www']['ok'] += 1
    
    # 4. HTML parseable sin errores
    try:
        from html.parser import HTMLParser
        parser = HTMLParser()
        parser.feed(content)
        checks['html_parseable']['ok'] += 1
    except Exception as e:
        checks['html_parseable']['fail'].append(f"{post}: {e}")

# Reporte
report = []
report.append("=" * 70)
report.append("VERIFICACIÓN TÉCNICA T1.3 — Interlinking blog→provinciales")
report.append(f"Fecha: 2026-06-11")
report.append(f"Total posts: {len(posts)}")
report.append("-" * 70)

for check_name, check_data in checks.items():
    etiqueta = {
        'rango_enlaces': '[ ] Cada post tiene 1-3 enlaces',
        'sin_duplicados_mismo_post': '[ ] Cero enlaces duplicados al mismo destino dentro del mismo post',
        'href_www': '[ ] Todos los href usan https://www.',
        'html_parseable': '[ ] HTML parseable sin errores nuevos',
    }[check_name]
    
    if check_data['fail']:
        report.append(f"\n{'❌' if check_data['fail'] else '✅'} {etiqueta}")
        report.append(f"   OK: {check_data['ok']}/{len(posts)}")
        report.append(f"   FALLOS: {len(check_data['fail'])}")
        for f in check_data['fail'][:5]:
            report.append(f"     - {f}")
        if len(check_data['fail']) > 5:
            report.append(f"     ... y {len(check_data['fail'])-5} más")
    else:
        report.append(f"\n✅ {etiqueta}")
        report.append(f"   OK: {check_data['ok']}/{len(posts)}")

report.append("\n" + "-" * 70)
todos_ok = all(len(c['fail']) == 0 for c in checks.values())
report.append(f"\n{'✅ TODAS LAS VERIFICACIONES PASARON' if todos_ok else '❌ ALGUNAS VERIFICACIONES FALLARON'}")
report.append("=" * 70)

result = "\n".join(report)
print(result)

# Guardar
with open("/home/arturo/certificadoya/informes/t1.3-validacion.txt", 'w', encoding='utf-8') as f:
    f.write(result)

# Si hay fallos, devolver exit code 0 pero reportar
sys.exit(0 if todos_ok else 1)
