import csv, re

rows = []
with open('C:/Users/artur/certificadoya/scripts/tecnicos_campana_20260801_master.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

SEDE_DOM = re.compile(r'(coaat|coat|cogiti|coitial|cogitial|coacyle|colegio|@coam)', re.I)
SEDE_ROL = re.compile(r'(admon|administracion|buzon|secretaria|correo@|coaatba@|decanosecretario|gestioneconomica|gestioncolegial|informatico|visados|pic@|abogado@)', re.I)
DUDOSO = re.compile(r'(musaat|sercover|caib\.es|@apps|wixpress|sentry|@payhip)', re.I)

tecnicos, sedes = [], []
for r in rows:
    e = r['email'].strip().lower()
    dom = e.split('@')[1]
    if DUDOSO.search(e):
        sedes.append(r)
    elif SEDE_DOM.search(dom) and (SEDE_ROL.search(e) or not re.search(r'aparejador\w*\.(com|es|net)$', dom)):
        sedes.append(r)
    else:
        tecnicos.append(r)

print(f"TECNICOS (campaña): {len(tecnicos)}")
print(f"NO TECNICOS (a CSV aparte): {len(sedes)}")

# Ordenar: primero personales (tecnicos claros), luego despachos
PERSONAL = re.compile(r'@(gmail|hotmail|yahoo|outlook|icloud)\.')
personales = [r for r in tecnicos if PERSONAL.search(r['email'])]
despachos = [r for r in tecnicos if not PERSONAL.search(r['email'])]

# Guardar master SOLO tecnicos
with open('C:/Users/artur/certificadoya/scripts/tecnicos_campana_20260801_master.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['email','despacho','provincia','nota'])
    w.writeheader()
    w.writerows(personales)
    w.writerows(despachos)

# Guardar sedes aparte
with open('C:/Users/artur/certificadoya/scripts/sedes_colegios_no_campana.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['email','despacho','provincia','nota'])
    w.writeheader()
    w.writerows(sedes)

print(f"\nMASTER FINAL: {len(tecnicos)} tecnicos")
print(f"  - personales (tecnicos claros): {len(personales)}")
print(f"  - despachos (parecen tecnicos): {len(despachos)}")
print(f"SEDES aparte: {len(sedes)} -> sedes_colegios_no_campana.csv")
