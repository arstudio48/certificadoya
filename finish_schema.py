#!/usr/bin/env python3
import re, os

RUTA = "C:/Users/artur/certificadoya"

NOMBRES = {
    'madrid':'Madrid','malaga':'M\u00e1laga','melilla':'Melilla','murcia':'Murcia',
    'navarra':'Navarra','ourense':'Ourense','palencia':'Palencia','pontevedra':'Pontevedra',
    'salamanca':'Salamanca','segovia':'Segovia','sevilla':'Sevilla','soria':'Soria',
    'tarragona':'Tarragona','tenerife':'Tenerife','teruel':'Teruel','toledo':'Toledo',
    'valencia':'Valencia','valladolid':'Valladolid','zamora':'Zamora','zaragoza':'Zaragoza'
}

for slug, prov in NOMBRES.items():
    fpath = f"{RUTA}/certificado-energetico-{slug}/index.html"
    if not os.path.exists(fpath):
        print(f"\u274c {slug}: no existe")
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'GEO-001:SCHEMA-INICIO' in content:
        print(f"\u23ed {slug}: ya tiene schema")
        continue
    
    schema = f'''  <!-- GEO-001:SCHEMA-INICIO -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Service",
    "name": "Certificado de Eficiencia Energ\u00e9tica en {prov}",
    "serviceType": "Certificaci\u00f3n energ\u00e9tica de edificios (CEE)",
    "areaServed": {{ "@type": "AdministrativeArea", "name": "{prov}" }},
    "provider": {{ "@type": "Organization", "name": "CertificadoYa.es", "url": "https://certificadoya.es" }}
  }}
  </script>
  <!-- GEO-001:SCHEMA-FIN -->
'''
    # Find Apple-touch-icon line (last in head) then insert schema
    marker = 'apple-touch-icon'
    if marker in content:
        content = content.replace(marker, marker + '\n' + schema, 1)
    else:
        content = content.replace('</head>', schema + '\n</head>', 1)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\u2705 {slug}: {prov}")

print("\n\u2705 Todas las 20 p\u00e1ginas procesadas")
