import csv, re

PERSONAL = re.compile(r'@(gmail|hotmail|yahoo|outlook|icloud|gmx|telefonica|ono|movistar)\.')

def load_csv(p):
    out = []
    with open(f'C:/Users/artur/certificadoya/scripts/{p}', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            e = (r.get('email') or '').strip().lower()
            if '@' not in e: continue
            out.append({'email': e, 'despacho': r.get('despacho',''), 'provincia': r.get('provincia',''), 'nota': r.get('nota','')})
    return out

# Existentes = pendientes actuales (167, ya priorizados personales primero)
pend = load_csv('tecnicos_pendientes_20260801.csv')
# Asturias = 977 nuevos
ast = load_csv('asturias_pdf_20260801.csv')

def prio(r):
    return 1 if PERSONAL.search(r['email']) else 2

# Clasificar en 4 grupos
pend_p1 = [r for r in pend if prio(r) == 1]
pend_p2 = [r for r in pend if prio(r) == 2]
ast_p1 = [r for r in ast if prio(r) == 1]
ast_p2 = [r for r in ast if prio(r) == 2]

print(f"Existentes: P1={len(pend_p1)} P2={len(pend_p2)}")
print(f"Asturias:   P1={len(ast_p1)} P2={len(ast_p2)}")

# Intercalar proporcionalmente: asturianos distribuidos uniformemente entre existentes
def intercalar(a, b):
    """a = existentes (sparse), b = asturianos (muchos). Intercala: a[0], b[0..k], a[1], b[k+1..2k]..."""
    out = []
    if not a:
        return b
    k = max(1, len(b) // len(a))  # cuántos b por cada a
    ia, ib = 0, 0
    while ia < len(a) or ib < len(b):
        if ia < len(a):
            out.append(a[ia]); ia += 1
        for _ in range(k):
            if ib < len(b):
                out.append(b[ib]); ib += 1
    return out

final = intercalar(pend_p1, ast_p1) + intercalar(pend_p2, ast_p2)
print(f"Total intercalado: {len(final)} (P1={sum(1 for r in final if prio(r)==1)} P2={sum(1 for r in final if prio(r)==2)})")

with open('C:/Users/artur/certificadoya/scripts/tecnicos_pendientes_20260801.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['email','despacho','provincia','nota'])
    w.writeheader(); w.writerows(final)

# Muestra: primeros 12 para ver el entrelazado
print("\n=== Primeros 12 (intercalado) ===")
for r in final[:12]:
    print(f"  {r['email']:55} | {r['nota'] or 'pend'}")
