import csv

SEDES_RONDA2 = {
    'info@coaat.es': ('COAAT Málaga', 'Málaga', 'patron_ronda2_sede'),
    'secretaria@coaathuesca.com': ('COAAT Huesca', 'Huesca', 'patron_ronda2_sede'),
}

master_path = 'C:/Users/artur/certificadoya/scripts/tecnicos_campana_20260801_master.csv'
sedes_path = 'C:/Users/artur/certificadoya/scripts/sedes_colegios_no_campana.csv'

with open(master_path, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
with open(sedes_path, encoding='utf-8') as f:
    sedes = list(csv.DictReader(f))

antes = len(rows)
rows = [r for r in rows if r['email'].strip().lower() not in SEDES_RONDA2]
quitados = antes - len(rows)

emails_sedes = {r['email'].strip().lower() for r in sedes}
for e, (desp, prov, nota) in SEDES_RONDA2.items():
    if e not in emails_sedes:
        sedes.append({'email': e, 'despacho': desp, 'provincia': prov, 'nota': nota})

with open(master_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['email','despacho','provincia','nota'])
    w.writeheader(); w.writerows(rows)
with open(sedes_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['email','despacho','provincia','nota'])
    w.writeheader(); w.writerows(sedes)

print(f"Master: {antes} -> {len(rows)} (quitadas {quitados} sedes)")
print(f"Sedes: {len(sedes)}")
