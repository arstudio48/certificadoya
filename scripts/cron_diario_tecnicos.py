#!/usr/bin/env python3
"""
cron_diario_tecnicos.py — Se ejecuta 1 vez al día.
Fase A: Busca NUEVOS técnicos CEE por patrón de dominio
Fase B: Envía 5-15 emails de captación
"""
import os, sys, json, csv, time, re, socket, random
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

socket.setdefaulttimeout(5)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# === TODOS LOS PATRONES VALIDADOS (incluye arquitectos, ingenieros, técnicos) ===
PATRONES = [
    # CEE directos (ya probados)
    "certificadoenergetico{c}",
    "certificado-energetico-{c}",
    "certificadosenergeticos{c}",
    "cee{c}",
    "eficienciaenergetica{c}",
    "tucertificado{c}",
    "certificadoenergetico{c}vivienda",
    # Aparejadores (ya probados, dan resultados)
    "aparejador{c}",
    "aparejadores{c}",
    "aparejador-{c}",
    # Arquitectos
    "arquitecto{c}",
    "arquitectos{c}",
    "arquitectura{c}",
    "arquitectotecnico{c}",
    # Ingenieros
    "ingeniero{c}",
    "ingenieros{c}",
    "ingenieria{c}",
    # Técnicos generales
    "tecnico{c}",
    "tecnicos{c}",
    "edificacion{c}",
    "gradoenedificacion{c}",
    # Estudios/despachos
    "estudio{c}",
    "estudios{c}",
    "proyectos{c}",
]

# Provincias + grandes municipios + sufijos comerciales
CIUDADES = [
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
    "santander","oviedo","elche","alcala","fuenlabrada","jerez",
    "marbella","benidorm","hospitalet","granollers","mataro",
    # Sufijos
    "online","barato","rapido","facil",
]

TLDS = [".es", ".com"]

# Keywords CEE para filtrar
CEE_KW = ['certificad', 'energetic', 'eficiencia', 'cee', 'etiqueta']

EMAIL_RE = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9._%+-]+@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_RE = re.compile(r'(?:\+34)?[ -]*(?:[679]\d{2}|[89]\d{2})[ -]*\d{2}[ -]*\d{2}[ -]*\d{2}')

BLACKLIST = ['example', 'tudominio', 'noreply', 'test@', 'demo@', 'ejemplo@',
             'your', 'youremail', 'mailinator', 'john@doe', 'misterello',
             'info@certificadosenergeticos.com', 'info@certificadoya.es',
             'tu@email', 'tu_correo@', 'empresa.com']

RUTAS = ["", "/contacto", "/contacto/", "/contacta", "/contact"]

BASE = os.path.expanduser('~/AppData/Local/hermes/scripts')
JSON_FILE = os.path.join(BASE, 'tecnicos_patrones.json')
CSV_FILE = os.path.join(BASE, 'tecnicos_captacion.csv')
EXCL_FILE = os.path.join(BASE, 'excluidos.txt')
SEND_SCRIPT = os.path.expanduser('~/certificadoya/scripts/envio_tecnicos.py')

PROV_MAP = {
    'alava':'Álava','albacete':'Albacete','alicante':'Alicante','almeria':'Almería',
    'asturias':'Asturias','avila':'Ávila','badajoz':'Badajoz','barcelona':'Barcelona',
    'burgos':'Burgos','caceres':'Cáceres','cadiz':'Cádiz','cantabria':'Cantabria',
    'castellon':'Castellón','ciudadreal':'Ciudad Real','cordoba':'Córdoba',
    'coruna':'A Coruña','cuenca':'Cuenca','girona':'Girona','granada':'Granada',
    'guadalajara':'Guadalajara','guipuzcoa':'Guipúzcoa','huelva':'Huelva',
    'huesca':'Huesca','jaen':'Jaén','leon':'León','lleida':'Lleida','lugo':'Lugo',
    'madrid':'Madrid','malaga':'Málaga','murcia':'Murcia','navarra':'Navarra',
    'ourense':'Ourense','palencia':'Palencia','palmas':'Las Palmas',
    'pontevedra':'Pontevedra','rioja':'La Rioja','salamanca':'Salamanca',
    'segovia':'Segovia','sevilla':'Sevilla','soria':'Soria','tarragona':'Tarragona',
    'tenerife':'Santa Cruz de Tenerife','teruel':'Teruel','toledo':'Toledo',
    'valencia':'Valencia','valladolid':'Valladolid','vizcaya':'Vizcaya',
    'zamora':'Zamora','zaragoza':'Zaragoza','bilbao':'Bilbao','gijon':'Gijón',
    'vigo':'Vigo','oviedo':'Oviedo','santander':'Santander','pamplona':'Pamplona',
    'san-sebastian':'San Sebastián','getafe':'Getafe','mostoles':'Móstoles',
    'alcorcon':'Alcorcón','sabadell':'Sabadell','terrassa':'Terrassa',
    'badalona':'Badalona','cartagena':'Cartagena','elche':'Elche',
    'jerez':'Jerez','marbella':'Marbella','benidorm':'Benidorm',
}

# ========== FASE A: BUSCAR NUEVOS CONTACTOS ==========

def check_domain(domain):
    for proto in ['https', 'http']:
        try:
            req = Request(f"{proto}://{domain}", headers=HEADERS)
            resp = urlopen(req, timeout=5)
            if resp.status < 400:
                html = resp.read().decode('utf-8', errors='replace').lower()
                return True, html
        except:
            continue
    return False, None

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

def detectar_provincia(dominio):
    dom = dominio.lower()
    mejor = ''
    for key in PROV_MAP:
        if key in dom and len(key) > len(mejor):
            mejor = key
    return PROV_MAP.get(mejor, '')

def fase_a():
    """Busca nuevos técnicos por patrón"""
    print(f"\n{'='*50}")
    print(f"FASE A: BÚSQUEDA DE NUEVOS TÉCNICOS")
    print(f"{'='*50}")
    
    # Generar candidatos
    candidatos = sorted(set(
        f"{p.replace('{c}', c)}{t}"
        for p in PATRONES
        for c in CIUDADES
        for t in TLDS
    ))
    
    # Cargar estado previo
    excluidos = set()
    if os.path.exists(EXCL_FILE):
        with open(EXCL_FILE) as f:
            excluidos = set(l.strip() for l in f if l.strip())
    
    previos = {}
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE) as f:
            for r in json.load(f):
                previos[r['dominio']] = r
    
    pendientes = [d for d in candidatos if d not in previos and d not in excluidos]
    
    print(f"Candidatos totales: {len(candidatos)}")
    print(f"Ya verificados: {len(previos)}")
    print(f"Nuevos a verificar: {len(pendientes)}")
    
    if not pendientes:
        print("✅ No hay nuevos dominios por verificar.")
        return 0
    
    resultados = list(previos.values())
    nuevos = 0
    t0 = time.time()
    
    for i, dom in enumerate(pendientes, 1):
        if i % 50 == 1 or i == len(pendientes):
            elapsed = time.time() - t0
            rate = i / max(elapsed, 0.1)
            rem = (len(pendientes) - i) / max(rate, 0.1)
            print(f"  [{i}/{len(pendientes)}] encontrados:{nuevos} | {elapsed:.0f}s | ~{rem:.0f}s rest | {dom}")
        
        ok, html = check_domain(dom)
        if not ok:
            with open(EXCL_FILE, 'a') as f: f.write(f"{dom}\n")
            continue
        
        tiene_cee = any(kw in (html or '') for kw in CEE_KW)
        emails, phones = extract(html)
        
        # Probar /contacto si no hay resultados
        if not emails and not phones:
            for ruta in RUTAS[1:]:
                try:
                    req = Request(f"https://{dom}{ruta}", headers=HEADERS)
                    resp = urlopen(req, timeout=4)
                    if resp.status < 400:
                        ch = resp.read().decode('utf-8', errors='replace').lower()
                        e2, p2 = extract(ch)
                        emails.update(e2)
                        phones.update(p2)
                        if not tiene_cee:
                            tiene_cee = any(kw in ch for kw in CEE_KW)
                        if emails or phones: break
                except: pass
        
        if tiene_cee or emails:
            resultados.append({
                'dominio': dom, 
                'tiene_cee': tiene_cee,
                'emails': sorted(emails), 
                'telefonos': sorted(phones),
                'timestamp': time.strftime('%Y-%m-%d'),
            })
            nuevos += 1
            if emails:
                print(f"    ✅ {dom} — {len(emails)} email(s)")
                for e in list(emails)[:2]:
                    print(f"       {e}")
            
            # Guardado incremental
            with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    t = time.time() - t0
    print(f"\nFase A: {nuevos} nuevos contactos en {t:.0f}s")
    
    # Re-generar CSV de captación
    regenerar_csv(resultados)
    return nuevos

def regenerar_csv(resultados):
    """Genera CSV limpio para la campaña"""
    seen = {}
    for r in resultados:
        for e in r.get('emails', []):
            if e not in seen:
                prov = detectar_provincia(r['dominio'])
                seen[e] = {
                    'email': e, 'dominio': r['dominio'],
                    'provincia': prov,
                    'tipo': 'institucional' if any(k in r['dominio'] for k in ['coaat','coac.','coam','cscae','coavn','apatgn','caat','entremuros','aparejador']) else 'personal',
                    'cee': r.get('tiene_cee', False),
                }
    
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['email','dominio','provincia','tipo','cee'])
        w.writeheader()
        for e in seen.values():
            w.writerow(e)
    
    print(f"CSV regenerado: {len(seen)} contactos únicos")
    return len(seen)

def fase_b():
    """Ejecuta el envío de 5-15 emails"""
    print(f"\n{'='*50}")
    print(f"FASE B: ENVÍO DE CAPTACIÓN")
    print(f"{'='*50}")
    
    if not os.path.exists(SEND_SCRIPT):
        print(f"❌ Script de envío no encontrado: {SEND_SCRIPT}")
        return
    
    import subprocess
    result = subprocess.run(
        [sys.executable, SEND_SCRIPT, '--send'],
        capture_output=True, text=True, timeout=600
    )
    print(result.stdout)
    if result.stderr:
        print(f"Errores: {result.stderr[:500]}")

if __name__ == '__main__':
    print(f"📅 CRON DIARIO — {time.strftime('%d/%m/%Y %H:%M')}")
    
    nuevos = fase_a()
    
    if nuevos > 0 or os.path.exists(CSV_FILE):
        fase_b()
    else:
        print("Sin novedades. Comprobando si hay pendientes de envío...")
        # Aún así ejecutar envío (puede haber pendientes de días anteriores)
        fase_b()
    
    print(f"\n✅ CRON COMPLETADO — {time.strftime('%H:%M:%S')}")
