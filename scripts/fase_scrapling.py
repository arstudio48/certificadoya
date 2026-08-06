"""
fase_scrapling.py — Scraping de foros técnicos y COAATs con anti-bot bypass
Usa Scrapling (curl_cffi + browserforge) para evitar bloqueos Cloudflare.
"""
import os, sys, re, json, csv, time, socket

BASE = os.path.expanduser('~/AppData/Local/hermes/scripts')
JSON_FILE = os.path.join(BASE, 'tecnicos_scrapling.json')
CSV_FILE = os.path.join(BASE, 'tecnicos_captacion.csv')
EXCL_FILE = os.path.join(BASE, 'excluidos_scrapling.txt')

EMAIL_RE = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9._%+-]+@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_RE = re.compile(r'(?:\+34)?[ -]*(?:[679]\d{2}|[89]\d{2})[ -]*\d{2}[ -]*\d{2}[ -]*\d{2}')

BLACKLIST = ['example', 'tudominio', 'noreply', 'test@', 'webmaster@', 'admin@',
             'tu@email', 'tu_correo@', 'empresa.com', 'soporte@', 'info@empresa',
             'error-lite@duckduckgo.com', 'hipotecas@rankia.com', 'ciudadano@idae.es',
             'empleo@habitissimo', 'mail@', '@domain.com']

CEE_KW = ['certificad', 'energetic', 'eficiencia', 'cee', 'etiqueta', 'calificación']

# Webs de COAATs y foros técnicos (antes bloqueados por Cloudflare)
OBJETIVOS = [
    # Foros profesionales (antes 403 con curl, ahora accesibles)
    ("Solo Arquitectura", "https://www.soloarquitectura.com/foros/", "foro"),
    ("Solo Arquitectura - Profesional", "https://www.soloarquitectura.com/foros/foro/arquitectura-tecnica-ejercicio-profesional.104/", "foro"),
    # COAATs accesibles
    ("COAAT Madrid", "https://www.aparejadormadrid.com/", "web"),
    ("COAAT Navarra", "https://www.coatnavarra.org/", "web"),
    ("COAAT Granada", "https://www.coaatgranada.com/", "web"),
    ("COAAT Asturias", "https://www.coaatasturias.com/", "web"),
    ("COAAT Valencia", "https://www.caatvalencia.es/", "web"),
    ("COAAT Barcelona", "https://www.apatgn.org/", "web"),
    ("COAAT Tarragona", "https://www.coattarragona.org/", "web"),
    ("COAAT Lleida", "https://www.coatlleida.cat/", "web"),
    ("COAAT Girona", "https://www.coatgirona.cat/", "web"),
    ("COAAT Canarias", "https://www.coatcanarias.com/", "web"),
    ("COAAT Murcia", "https://www.coatmurcia.com/", "web"),
    ("COAAT Galicia", "https://www.coatgalicia.es/", "web"),
    ("COAAT Córdoba", "https://www.coaatcordoba.es/", "web"),
    # Foros de energía
    ("Nergiza Foro", "https://nergiza.com/foro/", "foro"),
]

def extraer_contactos(html):
    emails, phones = set(), set()
    if not html: return emails, phones
    for m in EMAIL_RE.finditer(html):
        e = m.group().strip().lower()
        if any(b in e for b in BLACKLIST): continue
        if not e.split('.')[-1].isalpha(): continue
        if len(e) > 60: continue
        emails.add(e)
    for m in PHONE_RE.finditer(html):
        d = re.sub(r'\D', '', m.group())
        if len(d) == 9 and d[0] in '6789':
            phones.add(f'+34 {d[:3]} {d[3:6]} {d[6:]}')
        elif len(d) == 11 and d.startswith('34') and d[2] in '6789':
            phones.add(f'+34 {d[2:5]} {d[5:8]} {d[8:]}')
    return emails, phones

def buscar_perfiles(html, dominio_base):
    """Busca enlaces a perfiles profesionales"""
    links = set()
    # LinkedIn
    for m in re.finditer(r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+', html):
        links.add(m.group().split('?')[0])
    # Twitter/X
    for m in re.finditer(r'https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9_]+', html):
        if '/status/' not in m.group():
            links.add(m.group().split('?')[0])
    # Webs de profesionales
    for m in re.finditer(r'https?://[a-zA-Z0-9][a-zA-Z0-9.-]+\.(?:es|com|eu|org)[^"<>\s,)]*', html):
        url = m.group().rstrip('/')
        if dominio_base not in url and 'google' not in url.lower() and 'facebook' not in url.lower():
            links.add(url)
    return links

def ejecutar():
    """Ejecuta scraping con Scrapling. Retorna nuevos contactos."""
    print(f"\n{'='*50}")
    print(f"FASE SCRAPLING 🕷️  (anti-bot bypass)")
    print(f"{'='*50}")
    
    from scrapling import Fetcher
    f = Fetcher()
    
    # Cargar estado previo
    previos = {}
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE) as f_json:
            for r in json.load(f_json):
                previos[r['nombre']] = r
    
    excluidos = set()
    if os.path.exists(EXCL_FILE):
        with open(EXCL_FILE) as f_excl:
            excluidos = set(l.strip() for l in f_excl if l.strip())
    
    # Cargar CSV para dedup
    emails_existentes = set()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE) as f_csv:
            for r in csv.DictReader(f_csv):
                emails_existentes.add(r.get('email', '').strip().lower())
    
    resultados = []
    nuevos_emails = set()
    total_perfiles = set()
    
    for nombre, url, tipo in OBJETIVOS:
        if nombre in previos or nombre in excluidos:
            continue
        
        print(f"  🔍 {nombre}...", end=' ', flush=True)
        try:
            r = f.get(url, timeout=12)
            html = r.body.decode('utf-8', errors='replace') if r.body else ''
            status = r.status
            
            if status != 200 or not html:
                print(f"❌ HTTP {status} ({len(html)}b)")
                continue
            
            emails, phones = extraer_contactos(html)
            perfiles = buscar_perfiles(html, url)
            total_perfiles.update(perfiles)
            
            # Si es un foro, buscar en hilos/posts
            if tipo == 'foro':
                # Buscar enlaces a hilos del foro
                hilos = set(re.findall(r'href=[\'"](/foros/threads/[^\'"]*)[\'"]', html))
                # Buscar más info en cada hilo (solo los primeros 5)
                for h in list(hilos)[:5]:
                    try:
                        hr = f.get(f"https://www.soloarquitectura.com{h}", timeout=8)
                        h_html = hr.body.decode('utf-8', errors='replace') if hr.body else ''
                        e2, p2 = extraer_contactos(h_html)
                        emails.update(e2); phones.update(p2)
                        perfiles2 = buscar_perfiles(h_html, url)
                        total_perfiles.update(perfiles2)
                    except: pass
            
            nuevos_local = [e for e in emails if e not in emails_existentes and e not in nuevos_emails]
            
            if nuevos_local or phones or perfiles:
                nuevos_emails.update(nuevos_local)
                print(f"✅ +{len(nuevos_local)} emails, {len(phones)} tel, {len(perfiles)} perfiles")
                for e in list(nuevos_local)[:3]:
                    print(f"       {e}")
            else:
                print(f"sin contactos ({len(html)}b)")
            
            resultados.append({
                'nombre': nombre, 'url': url, 'tipo': tipo,
                'emails': sorted(emails), 'telefonos': sorted(phones),
                'perfiles': sorted(perfiles),
                'tiene_cee': any(kw in html.lower() for kw in CEE_KW),
                'status': status, 'size': len(html),
                'timestamp': time.strftime('%Y-%m-%d'),
            })
            
            # Guardado incremental
            with open(JSON_FILE, 'w', encoding='utf-8') as f_json:
                json.dump(resultados, f_json, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            with open(EXCL_FILE, 'a') as f_e: f_e.write(f"{nombre}\n")
    
    print(f"\n📊 SCRAPLING: {len(nuevos_emails)} emails nuevos, {len(total_perfiles)} perfiles")
    
    # Añadir al CSV
    if nuevos_emails:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f_csv:
            w = csv.writer(f_csv)
            for e in nuevos_emails:
                w.writerow([e, '', '', 'scrapling', 'personal', False])
        print(f"   Añadidos {len(nuevos_emails)} al CSV")
    
    return nuevos_emails

if __name__ == '__main__':
    ejecutar()
