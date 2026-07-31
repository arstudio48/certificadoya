import json, re, csv

records = json.load(open('C:/Users/artur/certificadoya/scripts/asturias_records.json', encoding='utf-8'))

# Correcciones manuales (truncados por salto de línea del PDF)
CORRECCIONES = {
    'josejoaquinfernandezalvarez@gmail.co': 'josejoaquinfernandezalvarez@gmail.com',
    '608956076certificacionenergeticamaria@gmail.comarquitecto': 'certificacionenergeticamaria@gmail.com',
    'rodriguezalvarez.eduardo@gmail.comingeniero': 'rodriguezalvarez.eduardo@gmail.com',
    '690655269beatriz@calificaeficienciaenergetica.comarquitecto': 'beatriz@calificaeficienciaenergetica.com',
    'ideya.sergio@gmail.co': 'ideya.sergio@gmail.com',
    'ignacio_martinez_gonzalez@hotmail.co': 'ignacio_martinez_gonzalez@hotmail.com',
    '657644682benjaminbustobarro@gmail.co': 'benjaminbustobarro@gmail.com',
    'ivan.junquera@gmail.': 'ivan.junquera@gmail.com',
    'luisalberto2105@hotmail': 'luisalberto2105@hotmail.com',
}

TYPOS = [
    ('gamil.com', 'gmail.com'), ('gmial.com', 'gmail.com'),
    ('hotmail.con', 'hotmail.com'), ('yahoo.con', 'yahoo.com'),
    ('gmaill.com', 'gmail.com'), ('hotmaill.com', 'hotmail.com'),
]

BAD = re.compile(r'(sentry|wixpress|payhip|\.png|\.jpg|\.webp|tudominio|ejemplo|@example|@test|@apps|noreply|usuario@|tu@email|su@email|@2x|@3x)', re.I)
ORGANISMO = re.compile(r'@(ayuntamiento|gob\.es|princast|asturias\.es|junta|gva\.es|gencat|xunta|aragon\.es|euskadi|madrid\.org|caib\.es|sede|registro|idepa|sade)', re.I)

def limpiar(e):
    e = e.strip().lower()
    if e in CORRECCIONES:
        e = CORRECCIONES[e]
    for a, b in TYPOS:
        if a in e:
            e = e.replace(a, b)
    return e

def valido(e):
    if '@' not in e: return False
    dom = e.split('@')[-1]
    if not re.search(r'\.(com|es|net|org|eu|cat|info|gal|biz|at)$', dom): return False
    if BAD.search(e): return False
    if ORGANISMO.search(e): return False
    if re.match(r'^[a-z0-9]+@[a-z0-9.-]+\.(com|es)$', e) and len(e.split('@')[0]) < 2: return False
    return True

nuevos_ast = {}
for r in records:
    e = limpiar(r['email'])
    if not valido(e): continue
    # Nota: despacho = nombre del técnico (del PDF)
    nombre = r['antes'].split(' | ')[-1] if r['antes'] else ''
    nuevos_ast.setdefault(e, {'despacho': nombre.title(), 'provincia': 'Asturias', 'nota': 'asturias_pdf'})

print(f"Asturias válidos tras limpieza: {len(nuevos_ast)}")

# Excluir duplicados con lo ya conocido (master + historial + smtp + pendientes)
conocidos = set()
for p in ['tecnicos_campana_20260801_master.csv', 'todos_tecnicos_priorizado.csv']:
    try:
        with open(f'C:/Users/artur/certificadoya/scripts/{p}', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if r.get('email'): conocidos.add(r['email'].strip().lower())
    except Exception: pass

hist = json.load(open('C:/Users/artur/certificadoya/scripts/.campana_suscripcion_history.json'))
for k in hist: conocidos.add(k.lower() if isinstance(k,str) else str(k).lower())

try:
    smtp = json.load(open('C:/Users/artur/certificadoya/scripts/.envio_tecnicos_history.json'))
    enviados = smtp.get('enviados', {}) if isinstance(smtp, dict) else {}
    for k in enviados: conocidos.add(k.lower())
except Exception: pass

dup = {e for e in nuevos_ast if e in conocidos}
print(f"Duplicados con lo ya conocido: {len(dup)}")
for e in sorted(dup)[:15]:
    print(f"  [DUP] {e}")

ast_final = {e: v for e, v in nuevos_ast.items() if e not in conocidos}
print(f"Asturias NUEVOS (a añadir): {len(ast_final)}")

with open('C:/Users/artur/certificadoya/scripts/asturias_pdf_20260801.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['email','despacho','provincia','nota'])
    w.writeheader()
    for e, v in sorted(ast_final.items()):
        w.writerow({'email': e, 'despacho': v['despacho'], 'provincia': v['provincia'], 'nota': v['nota']})

print(f"Guardado: asturias_pdf_20260801.csv ({len(ast_final)})")
