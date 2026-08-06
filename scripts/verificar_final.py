import csv, re

path = 'C:/Users/artur/certificadoya/scripts/tecnicos_pendientes_20260801.csv'
rows = list(csv.DictReader(open(path, encoding='utf-8')))

EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
BAD = re.compile(r'(sentry|wixpress|payhip|\.png|\.jpg|\.webp|tudominio|ejemplo|@example|@test|@apps|noreply|usuario@|tu@email|su@email|mail@example|youremail)', re.I)

vistos = set()
invalidos = []
basura = []
dups = 0
p1 = 0
for r in rows:
    e = r['email'].strip().lower()
    if not EMAIL.match(e):
        invalidos.append(e)
    elif BAD.search(e):
        basura.append(e)
    if e in vistos:
        dups += 1
    vistos.add(e)
    if re.search(r'@(gmail|hotmail|yahoo|outlook|icloud|gmx|telefonica|ono|movistar)\.', e):
        p1 += 1

print(f"Total: {len(rows)}")
print(f"P1 personales: {p1}")
print(f"P2 despachos: {len(rows)-p1}")
print(f"Duplicados: {dups}")
print(f"Inválidos: {len(invalidos)}")
for e in invalidos[:10]: print(f"  {e}")
print(f"Basura: {len(basura)}")
for e in basura[:10]: print(f"  {e}")

# Distribución por provincia
from collections import Counter
prov = Counter(r['provincia'] or '?' for r in rows)
print(f"\nProvincias: {dict(prov.most_common(10))}")

# Asturias vs resto
ast = sum(1 for r in rows if r['nota'] == 'asturias_pdf')
print(f"Asturias PDF: {ast} | Resto: {len(rows)-ast}")
