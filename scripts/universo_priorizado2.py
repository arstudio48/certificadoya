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

# Dominios de colegio
SEDE_DOM = re.compile(r'@(coaat|coat|cogiti|coitial|cogitial|coacyle|colegio|coam)\w*\.', re.I)
# Roles administrativos = sede
SEDE_ROL = re.compile(r'^(admon|administracion|buzon|secretaria|correo|decanosecretario|gestioneconomica|gestioncolegial|informatico|visados|pic|abogado|info|administracio|secretariotecnico|secretariatecnica)@', re.I)
DUDOSO = re.compile(r'(musaat|sercover|caib\.es|@apps|wixpress|sentry|@payhip)', re.I)
PERSONAL = re.compile(r'@(gmail|hotmail|yahoo|outlook|icloud)\.')

def clasificar(e):
    """Devuelve 1=personal tecnico, 2=despacho, 3=sede, 4=dudoso"""
    dom = e.split('@')[1]
    if DUDOSO.search(e): return 4
    if SEDE_DOM.search(dom):
        if SEDE_ROL.search(e): return 3  # rol admin en colegio = sede
        local = e.split('@')[0]
        if re.match(r'^[a-z]+\.[a-z]+$', local) or re.match(r'^[a-z]+\d*$', local):
            return 1  # nombre personal en colegio = tecnico colegiado
        return 3
    if PERSONAL.search(e): return 1
    return 2

vistos = {}
for r in master + hist + smtp:
    e = r['email'].strip().lower()
    if '@' not in e or e in vistos: continue
    vistos[e] = r

p1, p2, p3, p4 = [], [], [], []
for e in vistos:
    c = clasificar(e)
    (p1 if c==1 else p2 if c==2 else p3 if c==3 else p4).append(e)

print(f"UNIVERSO: {len(vistos)}")
print(f"  PRIORIDAD 1 - tecnicos personales/colegiados: {len(p1)}")
print(f"  PRIORIDAD 2 - despachos: {len(p2)}")
print(f"  EXCLUIDOS - sedes institucionales: {len(p3)}")
print(f"  EXCLUIDOS - dudosos: {len(p4)}")

print("\n=== Sedes institucionales (excluidas) ===")
for e in sorted(p3): print(f"  {e}")
print("\n=== Dudosos ===")
for e in sorted(p4): print(f"  {e}")

with open('C:/Users/artur/certificadoya/scripts/todos_tecnicos_priorizado.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['email', 'prioridad', 'tipo'])
    for e in p1: w.writerow([e, 1, 'tecnico'])
    for e in p2: w.writerow([e, 2, 'despacho'])
print(f"\nGuardado: todos_tecnicos_priorizado.csv ({len(p1)+len(p2)} tecnicos | {len(p3)+len(p4)} excluidos)")
