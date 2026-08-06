"""
fase_foros_chats.py — Módulo de scraping de foros y chats para técnicos CEE
Se ejecuta como parte del cron diario. Busca en fuentes accesibles:
  1. Reddit r/Spain (hilos CEE)
  2. Rankia (foro CEE público)
  3. Páginas Amarillas (directorios)
  4. Google My Business (vía resultados de búsqueda)
  5. LinkedIn perfiles públicos (vía Google)
  6. Telegram (canales públicos mencionados en la web)
"""
import os, sys, re, json, time, csv, socket
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

socket.setdefaulttimeout(8)
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
BASE = os.path.expanduser('~/AppData/Local/hermes/scripts')
JSON_FILE = os.path.join(BASE, 'tecnicos_foros_chats.json')
CSV_FILE = os.path.join(BASE, 'tecnicos_captacion.csv')
EXCL_FILE = os.path.join(BASE, 'excluidos_foros.txt')

EMAIL_RE = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9._%+-]+@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_RE = re.compile(r'(?:\+34)?[ -]*(?:[679]\d{2}|[89]\d{2})[ -]*\d{2}[ -]*\d{2}[ -]*\d{2}')

BLACKLIST = ['example', 'tudominio', 'noreply', 'test@', 'demo@', 'ejemplo@',
             'your', 'youremail', 'mailinator', 'john@doe', '@domain.com',
             'info@certificadoya.es', 'tu@email', 'tu_correo@', 'empresa.com']

CEE_KW = ['certificad', 'energetic', 'eficiencia', 'cee', 'etiqueta', 'calificación']

# ===== FUENTES =====

FUENTES = {
    # Reddit - secciones donde hablan de CEE
    "reddit_cee": {
        "url": "https://old.reddit.com/r/askspain/search?q=certificado+energetico&sort=new&restrict_sr=on",
        "tipo": "foro",
    },
    "reddit_spain_cee": {
        "url": "https://old.reddit.com/r/Spain/search?q=certificado+energetico+tecnico&sort=new&restrict_sr=on",
        "tipo": "foro",
    },
    "reddit_spain_ee": {
        "url": "https://old.reddit.com/r/Spain/search?q=eficiencia+energetica+certificacion&sort=new&restrict_sr=on",
        "tipo": "foro",
    },
    # Páginas Amarillas - directorio de técnicos
    "paginas_amarillas_madrid": {
        "url": "https://www.paginasamarillas.es/search/certificados%20energeticos/all-ma/1",
        "tipo": "directorio",
    },
    "paginas_amarillas_bcn": {
        "url": "https://www.paginasamarillas.es/search/certificados%20energeticos/all-b/1",
        "tipo": "directorio",
    },
    "paginas_amarillas_val": {
        "url": "https://www.paginasamarillas.es/search/certificados%20energeticos/all-v/1",
        "tipo": "directorio",
    },
    "paginas_amarillas_sev": {
        "url": "https://www.paginasamarillas.es/search/certificados%20energeticos/all-se/1",
        "tipo": "directorio",
    },
    # Google results for LinkedIn CEE profiles
    "google_linkedin": {
        "url": "https://lite.duckduckgo.com/lite/?q=site%3Alinkedin.com+%22t%C3%A9cnico+certificador%22+energ%C3%A9tico+Espa%C3%B1a",
        "tipo": "linkedin",
    },
    # Rankia foro CEE (lectura)
    "rankia_cee": {
        "url": "https://www.rankia.com/foro/certificado-de-eficiencia-energetica",
        "tipo": "foro",
    },
    # Telegram channel search
    "telegram_cee": {
        "url": "https://t.me/s/ceeespana",
        "tipo": "chat",
    },
    # Directorio técnicos IVACE
    "ivace_tecnicos": {
        "url": "https://gcee.aven.es/es/tecnicos-certificadores",
        "tipo": "directorio",
    },
    # Google search: technicians offering services
    "google_tecnicos": {
        "url": "https://lite.duckduckgo.com/lite/?q=%22t%C3%A9cnico+certificador%22+%22eficiencia+energ%C3%A9tica%22+%40gmail",
        "tipo": "directorio",
    },
    # COAAT profiles with emails
    "coaat_profiles": {
        "url": "https://lite.duckduckgo.com/lite/?q=site%3Acoaat.es+email+certificado+energetico",
        "tipo": "directorio",
    },
}

def fetch(url, timeout=8):
    try:
        req = Request(url, headers=HEADERS)
        resp = urlopen(req, timeout=timeout)
        data = resp.read()
        for enc in ['utf-8', 'latin-1', 'cp1252']:
            try: return data.decode(enc)
            except: continue
        return data.decode('utf-8', errors='replace')
    except Exception as e:
        return None

def extract_contacts(html):
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

def extract_from_reddit(html):
    """Extrae datos de old.reddit.com"""
    emails, phones = extract_contacts(html)
    # Buscar usuarios de Reddit (quizás tienen email en descripción)
    # También buscar enlaces a webs personales en los posts
    webs = set(re.findall(r'https?://[a-zA-Z0-9.-]+\.(?:es|com|eu)[^"<>\s]*', html or ''))
    return emails, phones, webs

def extract_from_paginas_amarillas(html):
    """Busca emails en páginas de directorio"""
    if not html: return set(), set()
    # Páginas Amarillas no muestra emails directamente, pero puede tener formularios
    # Buscar teléfonos (que sí muestra) como señal de técnico activo
    phones = set()
    for m in PHONE_RE.finditer(html):
        d = re.sub(r'\D', '', m.group())
        if len(d) == 9 and d[0] in '6789':
            phones.add(f'+34 {d[:3]} {d[3:6]} {d[6:]}')
    # Intentar encontrar emails directamente
    emails, _ = extract_contacts(html)
    return emails, phones

def tiene_cee_content(html):
    if not html: return False
    return any(kw in html.lower() for kw in CEE_KW)

def buscar_enlaces_perfiles(html, dominio):
    """Busca enlaces a perfiles de LinkedIn, Twitter, webs de técnicos"""
    if not html: return set()
    links = set()
    # LinkedIn
    for m in re.finditer(r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+', html):
        links.add(m.group().split('?')[0])
    # Twitter/X
    for m in re.finditer(r'https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9_]+', html):
        if '/status/' not in m.group():
            links.add(m.group().split('?')[0])
    # Webs
    for m in re.finditer(r'https?://[a-zA-Z0-9][a-zA-Z0-9.-]+\.(?:es|com|eu)[^"<>\s,)]*', html):
        if dominio not in m.group():
            links.add(m.group().rstrip('/'))
    return links

# ===== FASE PRINCIPAL =====

def ejecutar():
    """Ejecuta la búsqueda en todas las fuentes. Retorna nuevos contactos."""
    print(f"\n{'='*50}")
    print(f"FASE FOROS Y CHATS 🗣️")
    print(f"{'='*50}")
    
    # Cargar estado previo
    previos = {}
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE) as f:
            for r in json.load(f):
                previos[r['fuente']] = r
    
    excluidos = set()
    if os.path.exists(EXCL_FILE):
        with open(EXCL_FILE) as f:
            excluidos = set(l.strip() for l in f if l.strip())
    
    # Cargar CSV actual para deduplicación
    emails_existentes = set()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE) as f:
            reader = csv.DictReader(f)
            for r in reader:
                emails_existentes.add(r.get('email', '').strip().lower())
    
    resultados = []
    nuevos_emails = set()
    total_links_perfiles = set()
    
    for nombre, info in FUENTES.items():
        if nombre in excluidos:
            continue
        
        if nombre in previos:
            print(f"  ⏭️  {nombre} — ya verificado")
            continue
        
        url = info['url']
        tipo = info['tipo']
        
        print(f"  🔍 {nombre} ({tipo})...", end=' ', flush=True)
        html = fetch(url, timeout=10)
        
        if not html:
            print("❌ no responde")
            continue
        
        content_ok = tiene_cee_content(html)
        emails, phones = extract_contacts(html)
        
        # Procesamiento específico por tipo
        perfiles = set()
        if tipo == 'foro':
            e2, p2, webs = extract_from_reddit(html)
            emails.update(e2); phones.update(p2)
            perfiles = webs
        elif tipo == 'directorio':
            e2, p2 = extract_from_paginas_amarillas(html)
            emails.update(e2); phones.update(p2)
        
        perfiles.update(buscar_enlaces_perfiles(html, nombre))
        total_links_perfiles.update(perfiles)
        
        nuevos_local = [e for e in emails if e not in emails_existentes and e not in nuevos_emails]
        
        if nuevos_local or phones:
            nuevos_emails.update(nuevos_local)
            print(f"✅ +{len(nuevos_local)} emails, {len(phones)} tel, {len(perfiles)} perfiles")
            for e in list(nuevos_local)[:3]:
                print(f"       {e}")
        else:
            print(f"sin novedades ({len(html)}b)")
        
        results_entry = {
            'fuente': nombre,
            'url': url,
            'tipo': tipo,
            'emails': sorted(emails),
            'telefonos': sorted(phones),
            'perfiles': sorted(perfiles),
            'tiene_cee': content_ok,
            'timestamp': time.strftime('%Y-%m-%d'),
            'size_bytes': len(html or ''),
        }
        resultados.append(results_entry)
        
        # Guardado incremental
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    # Resultado
    print(f"\n📊 FOROS Y CHATS: {len(nuevos_emails)} emails nuevos, {len(total_links_perfiles)} perfiles encontrados")
    
    # Si hay nuevos emails, consolidar con CSV
    if nuevos_emails:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            for e in nuevos_emails:
                w.writerow([e, '', '', 'foro_chat', 'personal', False])
        print(f"   Añadidos {len(nuevos_emails)} al CSV de captación")
    
    return nuevos_emails

if __name__ == '__main__':
    ejecutar()
