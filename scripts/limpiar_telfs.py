import csv, re

path = 'C:/Users/artur/certificadoya/scripts/tecnicos_pendientes_20260801.csv'
with open(path, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Quitar prefijo de teléfono pegado: 7-9 dígitos al inicio del email
TELEF_PREF = re.compile(r'^(\d{7,9})([a-z][a-z0-9._%+-]*@)')
# Quitar sufijo de teléfono pegado tras el email (ej: x@gmail.com984191815)
TELEF_SUF = re.compile(r'(@[a-z0-9.-]+\.[a-z]{2,})(\d{6,9})$')
# Local que es solo teléfono con @dominio (985372979@telefonica.net) -> descartar? no, dejar

fixes = 0
clean = []
for r in rows:
    e = r['email'].strip()
    orig = e
    m = TELEF_PREF.match(e)
    if m:
        e = m.group(2)
    m2 = TELEF_SUF.search(e)
    if m2:
        e = e[:m2.start(2)]
    if e != orig:
        fixes += 1
        r['email'] = e
        r['nota'] = (r['nota'] or '') + '_telfix'
    clean.append(r)

print(f"Corregidos con teléfono pegado: {fixes}")
for r in clean:
    if '_telfix' in (r['nota'] or ''):
        print(f"  {r['email']}")

# Re-verificar duplicados tras limpieza
vistos = {}
dups = 0
final = []
for r in clean:
    e = r['email'].strip().lower()
    if e in vistos:
        dups += 1
        continue
    vistos[e] = True
    r['email'] = e
    final.append(r)

print(f"Tras limpieza: {len(final)} (dups eliminados: {dups})")

with open(path, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['email','despacho','provincia','nota'])
    w.writeheader(); w.writerows(final)

# También limpiar el CSV asturias_pdf para referencia
path2 = 'C:/Users/artur/certificadoya/scripts/asturias_pdf_20260801.csv'
with open(path2, encoding='utf-8') as f:
    rows2 = list(csv.DictReader(f))
for r in rows2:
    e = r['email'].strip()
    m = TELEF_PREF.match(e)
    if m: r['email'] = m.group(2)
    m2 = TELEF_SUF.search(r['email'])
    if m2: r['email'] = r['email'][:m2.start(2)]
with open(path2, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['email','despacho','provincia','nota'])
    w.writeheader(); w.writerows(rows2)
print(f"asturias_pdf limpio: {len(rows2)}")
