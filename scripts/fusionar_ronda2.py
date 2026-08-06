import csv, json, re

candidatos = []
with open('C:/Users/artur/certificadoya/scripts/enjambre_patrones_ronda2_20260801.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        e = (r.get('email') or '').strip().lower()
        if e: candidatos.append({'email': e, 'dom': r.get('despacho','')})

print("Candidatos:", len(candidatos))

# Conocidos: master + historial + smtp
master = set()
with open('C:/Users/artur/certificadoya/scripts/tecnicos_campana_20260801_master.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        if r.get('email'): master.add(r['email'].strip().lower())
hist = set(json.load(open('C:/Users/artur/certificadoya/scripts/.campana_suscripcion_history.json')))
try:
    smtp = json.load(open('C:/Users/artur/certificadoya/scripts/.envio_tecnicos_history.json'))
    smtp_emails = set(k.lower() for k in smtp.get('enviados', {}).keys())
except Exception:
    smtp_emails = set()
conocidos = master | hist | smtp_emails

# Basura / placeholders
BAD = re.compile(r'(%20|mail@example|tu_correo|youremail|tudominio|ejemplo|test@|noreply|sentry|wixpress|@apps|usuario@|su@email)', re.I)

nuevos = []
for c in candidatos:
    e = c['email']
    if e in conocidos:
        print(f"  [DUP] {e} ({c['dom']})")
        continue
    if BAD.search(e):
        print(f"  [BASURA] {e} ({c['dom']})")
        continue
    print(f"  [NUEVO] {e} ({c['dom']})")
    nuevos.append({'email': e, 'despacho': c['dom'], 'provincia': '', 'nota': 'patron_ronda2'})

print(f"\nNuevos válidos: {len(nuevos)}")

# Fusionar
master_path = 'C:/Users/artur/certificadoya/scripts/tecnicos_campana_20260801_master.csv'
with open(master_path, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
emails_master = {r['email'].strip().lower() for r in rows}
añadidos = 0
for n in nuevos:
    if n['email'] not in emails_master:
        rows.append(n)
        emails_master.add(n['email'])
        añadidos += 1

with open(master_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['email','despacho','provincia','nota'])
    w.writeheader(); w.writerows(rows)

print(f"MASTER: {len(rows)} técnicos (+{añadidos})")
