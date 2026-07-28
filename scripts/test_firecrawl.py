#!/usr/bin/env python3
import urllib.request, json, sys

url = 'http://localhost:3002/v0/scrape'
payload = json.dumps({
    'url': 'https://certificadodeeficienciaenergetica.com/lista-profesionales',
    'formats': ['markdown'],
    'onlyMainContent': False
}).encode()

try:
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req, timeout=30)
    d = json.loads(resp.read())
    
    if d.get('success'):
        md = d.get('data', {}).get('markdown', '')
        print(f'Longitud: {len(md)} chars')
        import re
        names = re.findall(r'###\s+\[([^\]]+)\]', md)
        print(f'Scrape OK - {len(names)} tecnicos')
        for n in names[:20]:
            print(f'  - {n}')
        if len(names) > 20:
            print(f'  ... y {len(names)-20} mas')
    else:
        print(f'Error: {d.get("error", "unknown")}')
except Exception as e:
    print(f'Exception: {e}')
