import json, re

records = json.load(open('C:/Users/artur/certificadoya/scripts/asturias_records.json', encoding='utf-8'))
uniq = {}
for r in records:
    e = r['email'].lower()
    uniq.setdefault(e, []).append(r)

def dominio_completo(e):
    dom = e.split('@')[-1]
    return bool(re.search(r'\.(com|es|net|org|eu|cat|info|gal)$', dom))

truncados = {e for e in uniq if not dominio_completo(e)}
print("=== TRUNCADOS (9) con contexto ===")
for e in truncados:
    ctx = uniq[e][0]
    print(f"  {e!r}")
    print(f"    antes: {ctx['antes'][-80:]}")
    print(f"    despues: {ctx['despues'][:60]}")

# Typos distintos de gamil
print("\n=== TYPOS no-gamil ===")
for e in uniq:
    if re.search(r'@gamil\.|@gmial\.', e): continue
    if not dominio_completo(e): continue
    if re.search(r'@hotmail\.(com|es)$', e): continue
    # posi bles typos: gmaill, hotmail.con, yaho, yahoo.con...
    if re.search(r'@(gmaill|hotmail\.con|yaho\.|yahoo\.con|outlock|hotmaill)\.', e):
        ctx = uniq[e][0]
        print(f"  {e!r} | {ctx['antes'][-60:]} | {ctx['despues'][:40]}")
