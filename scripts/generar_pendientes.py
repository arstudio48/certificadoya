import json, re, csv

def load_master():
    out = []
    with open('C:/Users/artur/certificadoya/scripts/tecnicos_campana_20260801_master.csv', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            out.append(r)
    return out

def load_hist():
    h = json.load(open('C:/Users/artur/certificadoya/scripts/.campana_suscripcion_history.json'))
    if isinstance(h, dict):
        return [{'email': k, 'nota': 'historial'} for k in h if '@' in str(k)]
    return [{'email': str(e), 'nota': 'historial'} for e in h if '@' in str(e)]

def load_smtp():
    try:
        s = json.load(open('C:/Users/artur/certificadoya/scripts/.envio_tecnicos_history.json'))
        enviados = s.get('enviados', s) if isinstance(s, dict) else s
        if isinstance(enviados, dict):
            return [{'email': k, 'nota': 'smtp'} for k in enviados if '@' in str(k)]
        return []
    except Exception:
        return []

master = load_master()
hist = load_hist()
smtp = load_smtp()

# Universo técnicos válidos (mismo criterio depurado: 87 P1 + 281 P2 = 368)
SEDE_DOM = re.compile(r'@(coaat|coat|cogiti|coitial|cogitial|coacyle|colegio|coam)\w*\.', re.I)
SEDE_ROL = re.compile(r'^(admon|administracion|buzon|secretaria|correo|decanosecretario|gestioneconomica|gestioncolegial|informatico|visados|pic|abogado|info|administracio|secretariotecnico|secretariatecnica)@', re.I)
DUDOSO = re.compile(r'(musaat|sercover|caib\.es|@apps|wixpress|sentry|@payhip)', re.I)
PERSONAL = re.compile(r'@(gmail|hotmail|yahoo|outlook|icloud)\.')

def es_tecnico_valido(e):
    dom = e.split('@')[1]
    if DUDOSO.search(e): return False
    if SEDE_DOM.search(dom):
        if SEDE_ROL.search(e): return False
        local = e.split('@')[0]
        if re.match(r'^[a-z]+\.[a-z]+$', local) or re.match(r'^[a-z]+\d*$', local): return True
        return False
    return True

def prioridad(e):
    if PERSONAL.search(e): return 1
    return 2

# Universo único
vistos = {}
for r in master + hist + smtp:
    e = r['email'].strip().lower()
    if '@' not in e or e in vistos: continue
    if not es_tecnico_valido(e): continue
    vistos[e] = r

# Ya lanzados (campaña + SMTP)
ya = set()
for r in hist: ya.add(r['email'].strip().lower())
for r in smtp: ya.add(r['email'].strip().lower())

pendientes = sorted([e for e in vistos if e not in ya], key=lambda e: (prioridad(e), e))

print(f"UNIVERSO técnicos válidos: {len(vistos)}")
print(f"Ya lanzados (campaña 198 + SMTP 45): {len(ya & set(vistos))}")
print(f"PENDIENTES de enviar: {len(pendientes)}")
print(f"  - P1 personales: {sum(1 for e in pendientes if prioridad(e)==1)}")
print(f"  - P2 despachos: {sum(1 for e in pendientes if prioridad(e)==2)}")

# Guardar CSV de pendientes
with open('C:/Users/artur/certificadoya/scripts/tecnicos_pendientes_20260801.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['email', 'despacho', 'provincia', 'nota'])
    for e in pendientes:
        r = vistos[e]
        w.writerow([e, r.get('despacho',''), r.get('provincia',''), r.get('nota','')])

print(f"\nGuardado: tecnicos_pendientes_20260801.csv ({len(pendientes)})")
