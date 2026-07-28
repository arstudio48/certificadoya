#!/usr/bin/env python3
"""
Extractor rápido de contactos de técnicos CEE.
Toma URLs, extrae emails/teléfonos con regex, guarda CSV.
"""
import re, csv, sys, socket, os
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

socket.setdefaulttimeout(10)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9',
}

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9._%+-]+@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_REGEX = re.compile(r'(?:\+34)?[ -]*(?:[679]\d{2}|[89]\d{2})[ -]*\d{2}[ -]*\d{2}[ -]*\d{2}')

BLACKLIST_DOMAIN = ['example', 'tudominio', 'dominio', 'email.com', '@email',
                    'noreply', 'no-reply', 'test@', 'demo@', 'ejemplo@',
                    'your', 'youremail', 'yourname', 'mailinator', 'yopmail']

def fetch(url):
    """Fetch URL content, return text or None"""
    try:
        req = Request(url, headers=HEADERS)
        resp = urlopen(req, timeout=10)
        data = resp.read()
        # Try common encodings
        for enc in ['utf-8', 'latin-1', 'cp1252']:
            try:
                return data.decode(enc)
            except:
                continue
        return data.decode('utf-8', errors='replace')
    except Exception as e:
        return None

def extract_emails(html):
    """Extract valid emails from HTML"""
    if not html:
        return []
    found = set()
    for match in EMAIL_REGEX.finditer(html):
        email = match.group().strip().lower()
        # Filter out garbage
        skip = False
        for b in BLACKLIST_DOMAIN:
            if b in email:
                skip = True
                break
        if skip:
            continue
        # Must have valid TLD
        if not email.split('.')[-1].isalpha():
            continue
        # Skip long unicode emails (garbage)
        if len(email) > 60:
            continue
        found.add(email)
    return sorted(found)

def extract_phones(html):
    """Extract Spanish phone numbers"""
    if not html:
        return []
    found = set()
    for match in PHONE_REGEX.finditer(html):
        phone = match.group().strip()
        # Clean up formatting
        phone_clean = re.sub(r'[ -]', '', phone)
        # Validate length (9 digits for ES)
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 9 and digits[0] in '6789':
            # Format nicely
            formatted = f'+34 {phone_clean[:3]} {phone_clean[3:6]} {phone_clean[6:]}'
            found.add(formatted)
        elif len(digits) == 11 and digits.startswith('34') and digits[2] in '6789':
            formatted = f'+34 {digits[2:5]} {digits[5:8]} {digits[8:]}'
            found.add(formatted)
    return sorted(found)

def scrape_source(name, urls):
    """Scrape a source and return results"""
    results = []
    print(f"\n{'='*50}")
    print(f"Fuente: {name}")
    print(f"{'='*50}")
    
    for url in urls:
        print(f"  Visitando: {url} ...", end=' ', flush=True)
        html = fetch(url)
        if html:
            emails = extract_emails(html)
            phones = extract_phones(html)
            if emails or phones:
                print(f"OK ({len(emails)} emails, {len(phones)} tel)")
                for e in emails:
                    results.append({'fuente': name, 'url': url, 'tipo': 'email', 'valor': e})
                    print(f"    📧 {e}")
                for p in phones:
                    results.append({'fuente': name, 'url': url, 'tipo': 'telefono', 'valor': p})
                    print(f"    📞 {p}")
            else:
                print("sin contactos")
        else:
            print("ERROR")
    return results

# === COAATs (colegios de aparejadores/arquitectos técnicos) ===
coats = [
    ("COAAT Madrid", ["https://www.coaat.es/", "https://www.coaat.es/contacto"]),
    ("COAAT Granada", ["https://www.coaatgranada.com/", "https://www.coaatgranada.com/contacto"]),
    ("COAAT Alicante", ["https://www.coatalicante.org/", "https://www.coatalicante.org/contacto"]),
    ("COAAT Coruña", ["https://www.coaatcoruna.org/", "https://www.coaatcoruna.org/contacto"]),
    ("COAAT Valladolid", ["https://www.coaatva.org/", "https://www.coaatva.org/contacto"]),
    ("COAAT Badajoz", ["https://www.coaatbadajoz.es/", "https://www.coaatbadajoz.es/contacto"]),
    ("COAAT Burgos", ["https://www.coatburgos.com/", "https://www.coatburgos.com/contacto"]),
    ("COAAT Cáceres", ["https://www.coaatcaceres.es/", "https://www.coaatcaceres.es/contacto"]),
    ("COAAT León", ["https://www.coatleon.org/", "https://www.coatleon.org/contacto"]),
    ("COAAT Salamanca", ["https://www.coatsalamanca.org/", "https://www.coatsalamanca.org/contacto"]),
    ("COAAT Vizcaya", ["https://www.coatvizcaya.com/", "https://www.coatvizcaya.com/contacto"]),
    ("COAAT Álava", ["https://www.coatalava.org/", "https://www.coatalava.org/contacto"]),
    ("COAAT Navarra", ["https://www.coatnavarra.org/", "https://www.coatnavarra.org/contacto"]),
    ("COAAT Zaragoza", ["https://www.coatzaragoza.org/", "https://www.coatzaragoza.org/contacto"]),
    ("COAAT Sevilla", ["https://www.coatsevilla.com/", "https://www.coatsevilla.com/contacto"]),
]

# === Empresas CEE directas ===
empresas_cee = [
    ("Certienergia", ["https://certienergia.com/", "https://certienergia.com/contacto"]),
    ("Tecnitasa", ["https://www.tecnitasa.es/", "https://www.tecnitasa.es/contacto"]),
    ("Certicalia", ["https://www.certicalia.com/contacto"]),
    ("CertificadoYa", ["https://www.certificadoya.es/contacto"]),
    ("Certificados Energéticos.com", ["https://www.certificadosenergeticos.com/contacto"]),
]

# === Directorios online ===
directorios = [
    ("Directorio CEE", ["https://certificadosenergetico.es/directorio"]),
    ("Aparejadores Madrid", ["https://www.aparejadoresmadrid.es/zona-ciudadanos/listado-expertos-certificacion"]),
    ("IVACE", ["https://gcee.aven.es/es/tecnicos-certificadores"]),
]

# === Ejecutar ===
all_results = []

for name, urls in coats:
    all_results.extend(scrape_source(name, urls))

for name, urls in empresas_cee:
    all_results.extend(scrape_source(name, urls))

for name, urls in directorios:
    all_results.extend(scrape_source(name, urls))

# === Guardar ===
if all_results:
    csv_path = os.path.expanduser('~/AppData/Local/hermes/scripts/contactos_tecnicos_cee.csv')
    json_path = os.path.expanduser('~/AppData/Local/hermes/scripts/contactos_tecnicos_cee.json')
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['fuente', 'url', 'tipo', 'valor'])
        w.writeheader()
        w.writerows(all_results)
    
    import json
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    emails = [r for r in all_results if r['tipo'] == 'email']
    phones = [r for r in all_results if r['tipo'] == 'telefono']
    
    print(f"\n{'='*50}")
    print(f"RESUMEN")
    print(f"{'='*50}")
    print(f"Total contactos: {len(all_results)}")
    print(f"  Emails: {len(emails)}")
    print(f"  Teléfonos: {len(phones)}")
    print(f"Guardado en: {csv_path}")
    
    # Print unique emails
    unique_emails = set(r['valor'] for r in emails)
    print(f"\nEmails únicos ({len(unique_emails)}):")
    for e in sorted(unique_emails):
        print(f"  {e}")
else:
    print("\nNo se encontraron contactos.")
    print("Los colegios suelen esconder los emails tras JS o formularios.")
    print("Para obtener técnicos individuales, recomiendo el método de")
    print("generación de dominios por patrón (ver skill).")
