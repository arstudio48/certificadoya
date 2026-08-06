#!/usr/bin/env python3
"""
FASE 2: Generación de dominios por patrón → técnicos CEE individuales.
Basado en método validado de la skill extractor-contactos-profesionales.
"""
import re, csv, json, os, sys, socket, time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

socket.setdefaulttimeout(8)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,*/*',
    'Accept-Language': 'es-ES,es;q=0.9',
}

# === PATRONES VALIDADOS (los que dieron resultados) ===
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
    "ingeniero{c}",
    "ingenieros{c}",
    "ingenieria{c}",
    "arquitecto{c}",
    "arquitectos{c}",
    "arquitectura{c}",
    "arquitectotecnico{c}",
    "edificacion{c}",
    "estudio{c}",
    "proyectos{c}",
    "tecnico{c}",
]

# === CIUDADES/PROVINCIAS (52 provincias + grandes municipios) ===
CIUDADES = [
    # Provincias
    "alava","albacete","alicante","almeria","asturias","avila","badajoz",
    "barcelona","burgos","caceres","cadiz","cantabria","castellon",
    "ciudadreal","cordoba","coruna","cuenca","girona","granada","guadalajara",
    "guipuzcoa","huelva","huesca","jaen","leon","lleida","lugo","madrid",
    "malaga","murcia","navarra","ourense","palencia","palmas","pontevedra",
    "rioja","salamanca","segovia","sevilla","soria","tarragona","tenerife",
    "teruel","toledo","valencia","valladolid","vizcaya","zamora","zaragoza",
    # Grandes municipios
    "getafe","mostoles","alcorcon","sabadell","terrassa","badalona",
    "cartagena","gijon","vigo","bilbao","san-sebastian","pamplona",
    "santander","granada","oviedo","elche","alcala","fuenlabrada","leganes",
    "jerez","马拉加","palma","almeria","huelva","marbella","benidorm",
    # Sufijos comerciales
    "online","barato","rapido","facil","madrid-online","barcelona-online",
]

TLDS = [".es", ".com"]

# Keywords para filtrar relevancia CEE
CEE_KEYWORDS = [
    'certificad', 'energetic', 'eficiencia', 'cee', 'etiqueta energetica',
    'calificacion', 'certificado', 'energia', 'ahorro', 'sostenible',
]

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9._%+-]+@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_REGEX = re.compile(r'(?:\+34)?[ -]*(?:[679]\d{2}|[89]\d{2})[ -]*\d{2}[ -]*\d{2}[ -]*\d{2}')

BLACKLIST_DOMAIN = ['example', 'tudominio', 'dominio', 'noreply', 'no-reply',
                    'test@', 'demo@', 'ejemplo@', 'your', 'youremail', 'mailinator',
                    'yopmail', 'john@doe', 'misterello100', 'info@certificadosenergeticos.com']

RESULTS_FILE = os.path.expanduser('~/AppData/Local/hermes/scripts/tecnicos_cee_patrones.json')
CSV_FILE = os.path.expanduser('~/AppData/Local/hermes/scripts/tecnicos_cee_patrones.csv')

def es_dominio_valido(dominio):
    """Verifica si el dominio existe y responde HTTP"""
    for url in [f"https://{dominio}", f"http://{dominio}"]:
        try:
            req = Request(url, headers=HEADERS)
            resp = urlopen(req, timeout=6)
            if resp.status < 400:
                text = resp.read().decode('utf-8', errors='replace').lower()
                # Verificar relevancia CEE
                tiene_cee = any(kw in text for kw in CEE_KEYWORDS)
                return True, url, text, tiene_cee
        except HTTPError as e:
            if e.code < 400:
                return True, url, "", False
        except:
            continue
    return False, None, None, None

def extraer_contactos(html, dominio):
    """Extrae emails y teléfonos del HTML"""
    if not html:
        return [], []
    
    emails = set()
    for m in EMAIL_REGEX.finditer(html):
        email = m.group().strip().lower()
        if any(b in email for b in BLACKLIST_DOMAIN):
            continue
        if not email.split('.')[-1].isalpha():
            continue
        if len(email) > 60:
            continue
        emails.add(email)
    
    phones = set()
    for m in PHONE_REGEX.finditer(html):
        digits = re.sub(r'\D', '', m.group())
        if len(digits) == 9 and digits[0] in '6789':
            phones.add(f'+34 {digits[:3]} {digits[3:6]} {digits[6:]}')
        elif len(digits) == 11 and digits.startswith('34') and digits[2] in '6789':
            phones.add(f'+34 {digits[2:5]} {digits[5:8]} {digits[8:]}')
    
    return sorted(emails), sorted(phones)

def fetch_url(url):
    """Fetch URL content"""
    try:
        req = Request(url, headers=HEADERS)
        resp = urlopen(req, timeout=8)
        data = resp.read()
        for enc in ['utf-8', 'latin-1', 'cp1252']:
            try:
                return data.decode(enc)
            except:
                continue
        return data.decode('utf-8', errors='replace')
    except:
        return None

def main():
    # Generar todos los candidatos
    candidatos = []
    for patron in PATRONES:
        for ciudad in CIUDADES:
            nombre = patron.replace('{c}', ciudad)
            for tld in TLDS:
                candidatos.append(f"{nombre}{tld}")
    
    # Quitar duplicados
    candidatos = sorted(set(candidatos))
    
    # Cargar resultados previos si existen
    resultados_previos = {}
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
                for r in json.load(f):
                    resultados_previos[r['dominio']] = r
        except:
            pass
    
    # Cargar excluidos previos
    excluidos = set()
    excl_file = os.path.expanduser('~/AppData/Local/hermes/scripts/excluidos_patrones.txt')
    if os.path.exists(excl_file):
        with open(excl_file) as f:
            excluidos = set(line.strip() for line in f if line.strip())
    
    total = len(candidatos)
    nuevos = [d for d in candidatos if d not in resultados_previos and d not in excluidos]
    print(f"Candidatos totales: {total}")
    print(f"Ya verificados: {len(resultados_previos)}")
    print(f"A verificar ahora: {len(nuevos)}")
    print(f"Tiempo estimado: ~{len(nuevos) * 2 // 60} min")
    print()
    
    resultados = list(resultados_previos.values())
    contador = 0
    exitosos = 0
    t_start = time.time()
    
    for dominio in nuevos:
        contador += 1
        
        # Progreso
        if contador % 25 == 0 or contador == 1:
            elapsed = time.time() - t_start
            rate = contador / elapsed if elapsed > 0 else 0
            remaining = (len(nuevos) - contador) / rate if rate > 0 else 0
            print(f"[{contador}/{len(nuevos)}] {exitosos} exitos | "
                  f"{elapsed:.0f}s trans | ~{remaining:.0f}s rest | "
                  f"Actual: {dominio}")
        
        valido, url, html, tiene_cee = es_dominio_valido(dominio)
        
        if valido:
            emails, phones = [], []
            
            if html:
                emails, phones = extraer_contactos(html, dominio)
            
            # Si no hay contactos, probar /contacto
            if not emails and not phones:
                contacto_url = url.rstrip('/') + '/contacto'
                contacto_html = fetch_url(contacto_url)
                if contacto_html:
                    ce, cp = extraer_contactos(contacto_html, dominio)
                    emails.extend(ce)
                    phones.extend(cp)
                    if ce or cp:
                        html = (html or '') + ' ' + contacto_html
                        # Re-evaluar CEE con el contenido del contacto
                        if not tiene_cee:
                            tiene_cee = any(kw in (contacto_html or '').lower() for kw in CEE_KEYWORDS)
            
            if emails or phones:
                exitosos += 1
                entry = {
                    'dominio': dominio,
                    'url': url,
                    'tiene_cee': tiene_cee,
                    'emails': emails,
                    'telefonos': phones,
                    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
                }
                resultados.append(entry)
                
                print(f"  ✅ {dominio} - {len(emails)} emails, {len(phones)} tel - CEE:{tiene_cee}")
                for e in emails[:3]:
                    print(f"     📧 {e}")
                
                # Guardar incremental
                with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(resultados, f, ensure_ascii=False, indent=2)
        else:
            # Guardar excluido para no reprocesar
            with open(excl_file, 'a') as f:
                f.write(f"{dominio}\n")
        
        # Pequeña pausa para no saturar
        if contador % 10 == 0:
            time.sleep(0.5)
    
    # === REPORTE FINAL ===
    t_total = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"FASE 2 COMPLETADA")
    print(f"{'='*60}")
    print(f"Total candidatos: {total}")
    print(f"Verificados ahora: {len(nuevos)}")
    print(f"Dominios existentes: {sum(1 for r in resultados if r['dominio'] in nuevos)}")
    print(f"Con contactos: {exitosos}")
    print(f"Tiempo: {t_total:.0f}s ({t_total/60:.1f} min)")
    print(f"Tasa exito: {exitosos/max(len(nuevos),1)*100:.1f}%")
    
    # Stats de contactos
    all_emails = set()
    all_phones = set()
    cee_relevantes = 0
    for r in resultados:
        all_emails.update(r.get('emails', []))
        all_phones.update(r.get('telefonos', []))
        if r.get('tiene_cee'):
            cee_relevantes += 1
    
    print(f"\n📊 CONTACTOS TOTALES:")
    print(f"  Emails únicos: {len(all_emails)}")
    print(f"  Teléfonos únicos: {len(all_phones)}")
    print(f"  Webs con keywords CEE: {cee_relevantes}/{len(resultados)}")
    
    # Guardar CSV final
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['dominio', 'tiene_cee', 'email', 'telefono'])
        for r in resultados:
            for e in r.get('emails', []):
                w.writerow([r['dominio'], r.get('tiene_cee', False), e, ''])
            for p in r.get('telefonos', []):
                w.writerow([r['dominio'], r.get('tiene_cee', False), '', p])
    
    print(f"\n📁 Ficheros guardados:")
    print(f"  JSON: {RESULTS_FILE}")
    print(f"  CSV:  {CSV_FILE}")
    
    # Mostrar emails únicos
    if all_emails:
        print(f"\n📧 EMAILS ({len(all_emails)}):")
        for e in sorted(all_emails)[:30]:
            print(f"  {e}")
        if len(all_emails) > 30:
            print(f"  ... y {len(all_emails)-30} más (ver CSV)")

if __name__ == '__main__':
    main()
