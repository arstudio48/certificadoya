import csv, re
from collections import Counter

rows = []
with open('C:/Users/artur/certificadoya/scripts/todos_tecnicos_priorizado.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append(r['email'])

# Provincias por dominio patrón (aparejadorX, arquitectotecnicoX, certificadoenergeticoX)
PROV = {
    'madrid':'Madrid','barcelona':'Barcelona','valencia':'Valencia','sevilla':'Sevilla','zaragoza':'Zaragoza',
    'malaga':'Málaga','murcia':'Murcia','palma':'Baleares','mallorca':'Baleares','menorca':'Baleares',
    'laspalmas':'Las Palmas','tenerife':'Tenerife','granada':'Granada','alicante':'Alicante','bilbao':'Bizkaia',
    'gipuzkoa':'Gipuzkoa','vitoria':'Álava','coruna':'A Coruña','lugo':'Lugo','pontevedra':'Pontevedra',
    'ourense':'Ourense','asturias':'Asturias','gijon':'Asturias','oviedo':'Asturias','cantabria':'Cantabria',
    'santander':'Cantabria','castellon':'Castellón','tarragona':'Tarragona','girona':'Girona','lleida':'Lleida',
    'salamanca':'Salamanca','valladolid':'Valladolid','burgos':'Burgos','leon':'León','zamora':'Zamora',
    'palencia':'Palencia','segovia':'Segovia','soria':'Soria','avila':'Ávila','toledo':'Toledo','cuenca':'Cuenca',
    'guadalajara':'Guadalajara','ciudadreal':'Ciudad Real','albacete':'Albacete','caceres':'Cáceres',
    'badajoz':'Badajoz','huelva':'Huelva','cadiz':'Cádiz','cordoba':'Córdoba','jaen':'Jaén','almeria':'Almería',
    'teruel':'Teruel','huesca':'Huesca','pamplona':'Navarra','navarra':'Navarra','larioja':'La Rioja','logrono':'La Rioja',
    'carabanchel':'Madrid','getafe':'Madrid','mostoles':'Madrid','alcorcon':'Madrid',
}
prov_counts = Counter()
for e in rows:
    dom = e.split('@')[1].replace('.es','').replace('.com','').replace('.net','').replace('.org','').replace('www.','')
    found = False
    for k, v in sorted(PROV.items(), key=lambda x: -len(x[0])):
        if k in dom:
            prov_counts[v] += 1
            found = True
            break
    if not found:
        prov_counts['(otro/extranjero)'] += 1

print(f"Total técnicos: {len(rows)}")
print("\n=== Cobertura por provincia ===")
for prov, n in prov_counts.most_common():
    bar = '#' * min(n, 40)
    print(f"  {prov:22} {n:3} {bar}")
