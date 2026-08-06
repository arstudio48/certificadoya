import csv, re

def load(p):
    out = []
    with open(p, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            if r.get('email'):
                out.append(r['email'].strip().lower())
    return out

master = load('C:/Users/artur/certificadoya/scripts/tecnicos_campana_20260801_master.csv')
sedes = load('C:/Users/artur/certificadoya/scripts/sedes_colegios_no_campana.csv')

print(f"Master: {len(master)} | Sedes: {len(sedes)}")
print(f"Duplicados en master: {len(master) - len(set(master))}")
print(f"Cruce master∩sedes: {len(set(master) & set(sedes))}")

# Validar formato
valido = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
invalidos = [e for e in master if not valido.match(e)]
print(f"Inválidos en master: {len(invalidos)} {invalidos[:5]}")

# Basura residual
bad = [e for e in master if re.search(r'(\.png|\.jpg|sentry|tudominio|ejemplo|test@|tu@email|@payhip|wixpress|\.pe$|\.ar$|\.it$|\.co\.uk$|@caib|musaat|sercover)', e)]
print(f"Basura residual en master: {len(bad)} {bad[:5]}")
