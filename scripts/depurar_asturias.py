import json, re

records = json.load(open('C:/Users/artur/certificadoya/scripts/asturias_records.json', encoding='utf-8'))

# Emails únicos
uniq = {}
for r in records:
    e = r['email'].lower()
    uniq.setdefault(e, []).append(r)

print("Emails únicos:", len(uniq))

# Detectar truncados (acaban sin TLD completo) y typos
TRUNCADO = re.compile(r'@[a-z0-9.-]+$')
def dominio_completo(e):
    # hotmail, gmail, yahoo, outlook... sin .com/.es = truncado
    dom = e.split('@')[-1]
    return bool(re.search(r'\.(com|es|net|org|eu|cat|info|gal)$', dom))

truncados = {e for e in uniq if not dominio_completo(e)}
typos = {e for e in uniq if re.search(r'@gamil\.|@gmial\.|@hotmial\.|@hotmail\.[^c]|@gmail\.[^c]|@yaoo\.|@yaho\.', e)}

print("Truncados sin TLD:", len(truncados))
print("Typos comunes:", len(typos))

# Corregir truncados de hotmail/gmail/yahoo (cortados por salto de línea)
def corregir(e):
    # Si el dominio es hotmail/gmail/yahoo/outlook sin TLD -> añadir .com
    if e.endswith('@hotmail') or e.endswith('@gmail') or e.endswith('@yahoo') or e.endswith('@outlook') or e.endswith('@hotmail.es'):
        return e + '.com' if not e.endswith('.es') else e
    return e

corregidos = {}
for e in uniq:
    c = corregir(e)
    if c != e:
        corregidos[e] = c

print("A corregir por truncamiento dominio:", len(corregidos))
for k, v in list(corregidos.items())[:20]:
    print(f"  {k} -> {v}")

# Typos gamil -> gmail
fix_typo = {}
for e in uniq:
    if 'gamil.com' in e: fix_typo[e] = e.replace('gamil.com','gmail.com')
    elif 'gmial.com' in e: fix_typo[e] = e.replace('gmial.com','gmail.com')
print("Typos a corregir:", len(fix_typo))
for k, v in list(fix_typo.items())[:10]:
    print(f"  {k} -> {v}")
