#!/usr/bin/env python3
"""
FASE 2 v2 — Solo patrones productivos de CEE.
Genera dominios, verifica existencia, extrae contactos.
Optimizado para velocidad (~4 min).
"""
import re, csv, json, os, sys, socket, time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

socket.setdefaulttimeout(4)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,*/*',
}

# Solo patrones que la skill validó como productivos
PATRONES = [
    "certificadoenergetico{c}",
    "certificado-energetico-{c}",
    "certificadosenergeticos{c}",
    "cee{c}",
    "eficienciaenergetica{c}",
    "tucertificado{c}",
    "certificadoenergetico{c}vivienda",
    "aparejador{c}",
    "aparejadores{c}",
    "aparejador-{c}",
]

# Provincias (código 2 letras + nombre común)
PROVINCIAS = [
    "alava","albacete","alicante","almeria","asturias","avila","badajoz",
    "barcelona","burgos","caceres","cadiz","cantabria","castellon",
    "ciudadreal","cordoba","coruna","cuenca","girona","granada","guadalajara",
    "guipuzcoa","huelva","huesca","jaen","leon","lleida","lugo","madrid",
    "malaga","murcia","navarra","ourense","palencia","palmas","pontevedra",
    "rioja","salamanca","segovia","sevilla","soria","tarragona","tenerife",
    "teruel","toledo","valencia","valladolid","vizcaya","zamora","zaragoza",
    "online","barato",
]

TLDS = [".es", ".com"]

CEE_KEYWORDS = ['certificad', 'energetic', 'eficiencia', 'cee', 'etiqueta']

EMAIL_RE = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9._%+-]+@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_RE = re.compile(r'(?:\+34)?[ -]*(?:[679]\d{2}|[89]\d{2})[ -]*\d{2}[ -]*\d{2}[ -]*\d{2}')

BLACKLIST = ['example', 'tudominio', 'noreply', 'test@', 'demo@', 'ejemplo@',
             'your', 'youremail', 'mailinator', 'john@doe', 'misterello',
             'info@certificadosenergeticos.com', 'info@certificadoya.es']

RUTAS = ["", "/contacto", "/contacto/", "/contacta", "/contact"]

def check_domain(domain):
    """Returns (exists, url, html)"""
    for proto in ['https', 'http']:
        url = f"{proto}://{domain}"
        try:
            req = Request(url, headers=HEADERS)
            resp = urlopen(req, timeout=4)
            if resp.status < 400:
                html = resp.read().decode('utf-8', errors='replace').lower()
                return True, url, html
        except:
            continue
    return False, None, None

def extract(text):
    emails, phones = set(), set()
    if not text: return emails, phones
    for m in EMAIL_RE.finditer(text):
        e = m.group().strip().lower()
        if any(b in e for b in BLACKLIST): continue
        if not e.split('.')[-1].isalpha(): continue
        if len(e) > 60: continue
        emails.add(e)
    for m in PHONE_RE.finditer(text):
        d = re.sub(r'\D', '', m.group())
        if len(d) == 9 and d[0] in '6789':
            phones.add(f'+34 {d[:3]} {d[3:6]} {d[6:]}')
        elif len(d) == 11 and d.startswith('34') and d[2] in '6789':
            phones.add(f'+34 {d[2:5]} {d[5:8]} {d[8:]}')
    return emails, phones

def main():
    # Generar candidatos
    candidatos = sorted(set(
        f"{p.replace('{c}', c)}{t}"
        for p in PATRONES
        for c in PROVINCIAS
        for t in TLDS
    ))
    
    # Cargar excluidos previos
    excl_file = os.path.expanduser('~/AppData/Local/hermes/scripts/excluidos.txt')
    excluidos = set()
    if os.path.exists(excl_file):
        with open(excl_file) as f:
            excluidos = set(l.strip() for l in f if l.strip())
    
    # Cargar resultados previos
    res_file = os.path.expanduser('~/AppData/Local/hermes/scripts/tecnicos_patrones.json')
    previos = {}
    if os.path.exists(res_file):
        with open(res_file) as f:
            for r in json.load(f):
                previos[r['dominio']] = r
    
    pendientes = [d for d in candidatos if d not in previos and d not in excluidos]
    
    print(f"Total candidatos: {len(candidatos)}")
    print(f"Ya verificados: {len(previos)}")
    print(f"A verificar ahora: {len(pendientes)}")
    print()
    
    resultados = list(previos.values())
    n_ok, n_cee = 0, 0
    t0 = time.time()
    
    for i, dom in enumerate(pendientes, 1):
        if i % 25 == 1 or i == len(pendientes):
            elapsed = time.time() - t0
            rate = i / max(elapsed, 0.1)
            rem = (len(pendientes) - i) / max(rate, 0.1)
            print(f"[{i}/{len(pendientes)}] OK:{n_ok} CEE:{n_cee} "
                  f"{elapsed:.0f}s | ~{rem:.0f}s | {dom}")
        
        ok, url, html = check_domain(dom)
        if not ok:
            with open(excl_file, 'a') as f: f.write(f"{dom}\n")
            continue
        
        # Verificar keywords CEE
        tiene_cee = any(kw in (html or '') for kw in CEE_KEYWORDS)
        
        emails, phones = extract(html)
        
        # Probar rutas de contacto si no hay resultados
        for ruta in RUTAS:
            if emails or phones: break
            if ruta:
                cu = url.rstrip('/') + ruta
                try:
                    req = Request(cu, headers=HEADERS)
                    resp = urlopen(req, timeout=4)
                    if resp.status < 400:
                        ch = resp.read().decode('utf-8', errors='replace').lower()
                        e2, p2 = extract(ch)
                        emails.update(e2)
                        phones.update(p2)
                        if not tiene_cee:
                            tiene_cee = any(kw in ch for kw in CEE_KEYWORDS)
                except:
                    pass
        
        if emails or phones or tiene_cee:
            entry = {
                'dominio': dom, 'url': url, 'tiene_cee': tiene_cee,
                'emails': sorted(emails), 'telefonos': sorted(phones),
            }
            resultados.append(entry)
            n_ok += 1
            if tiene_cee: n_cee += 1
            
            if emails:
                print(f"  ✅ {dom} — {len(emails)} email(s)")
                for e in list(emails)[:3]:
                    print(f"     {e}")
            
            # Guardado incremental
            with open(res_file, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    # Reporte final
    t = time.time() - t0
    print(f"\n{'='*50}")
    print(f"FASE 2 COMPLETADA")
    print(f"{'='*50}")
    print(f"Candidatos: {len(candidatos)}")
    print(f"Verificados: {len(pendientes)} en {t:.0f}s")
    print(f"Con contacto: {n_ok} ({n_ok/max(len(pendientes),1)*100:.1f}%)")
    print(f"Relevantes CEE: {n_cee}")
    
    all_emails = set()
    for r in resultados:
        all_emails.update(r.get('emails', []))
    
    csv_file = os.path.expanduser('~/AppData/Local/hermes/scripts/tecnicos_patrones.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['dominio','cee','email','telefono'])
        for r in resultados:
            for e in r.get('emails', []):
                w.writerow([r['dominio'], r.get('tiene_cee',''), e, ''])
            for p in r.get('telefonos', []):
                w.writerow([r['dominio'], r.get('tiene_cee',''), '', p])
    
    print(f"\n📧 Emails únicos: {len(all_emails)}")
    for e in sorted(all_emails)[:40]:
        print(f"  {e}")
    print(f"\n📁 CSV: {csv_file}")

if __name__ == '__main__':
    main()
