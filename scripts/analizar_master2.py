import csv, re

rows = []
with open('C:/Users/artur/certificadoya/scripts/tecnicos_campana_20260801_master.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Sedes de colegios = dominio coaat/coat/cogiti/coacyle + rol institucional
SEDE_DOM = re.compile(r'(coaat|coat|cogiti|coitial|cogitial|coacyle|colegio|@coam)', re.I)
SEDE_ROL = re.compile(r'(admon|administracion|buzon|secretaria|correo@|coaatba@|decanosecretario|gestioneconomica|gestioncolegial|informatico|visados|pic@|abogado@)', re.I)

# Dudosos: mutuas, empresas de servicios, administración
DUDOSO = re.compile(r'(musaat|sercover|caib\.es|@apps|wixpress|sentry|@payhip)', re.I)

sedes, dudosos, despachos, personales = [], [], [], []
for r in rows:
    e = r['email'].strip().lower()
    dom = e.split('@')[1]
    if DUDOSO.search(e):
        dudosos.append(r)
    elif SEDE_DOM.search(dom) and (SEDE_ROL.search(e) or SEDE_DOM.search(dom) and not re.search(r'aparejador\w*\.(com|es|net)$', dom)):
        sedes.append(r)
    elif re.search(r'@(gmail|hotmail|yahoo|outlook|icloud)\.', e):
        personales.append(r)
    else:
        despachos.append(r)

print(f"TOTAL: {len(rows)}")
print(f"A) TECNICOS REALES (personales gmail/hotmail): {len(personales)}")
print(f"B) DESPACHOS/ESTUDIOS (dominio propio): {len(despachos)}")
print(f"C) SEDES DE COLEGIO (institucional, no firman): {len(sedes)}")
print(f"D) DUDOSOS (mutua/aseguradora/admin): {len(dudosos)}")

print("\n=== C) SEDES COLEGIO — estas NO son tecnicos ===")
for r in sedes:
    print(f"  {r['email']} | {r.get('despacho','')}")

print("\n=== D) DUDOSOS ===")
for r in dudosos:
    print(f"  {r['email']} | {r.get('despacho','')}")

print("\n=== A) PERSONALES (si, tecnicos) ===")
for r in personales:
    print(f"  {r['email']} | {r.get('despacho','')}")
