import fitz, re

doc = fitz.open('C:/Users/artur/certificadoya/scripts/.hermes/desktop-attachments/Listado de técnicos cualificados registrados (8 de enero de 2024).pdf')
full = []
for page in doc:
    full.append(page.get_text())
text = '\n'.join(full)
open('C:/Users/artur/certificadoya/scripts/asturias_tecnicos_bruto.txt','w',encoding='utf-8').write(text)

# Los registros van en bloques: nombre, apellidos, tlfs, email, titulacion, nº registro
# Patrón: email seguido de titulación y nº registro 0000XXX T
lines = [l.strip() for l in text.split('\n') if l.strip()]

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
emails = EMAIL_RE.findall(text)
print("Emails crudos encontrados:", len(emails))

# Registrar contexto por email: buscar el bloque anterior (nombre/apellidos) y posterior (titulación)
records = []
for i, l in enumerate(lines):
    m = EMAIL_RE.search(l)
    if not m: continue
    email = m.group(0)
    # Nombre: buscar hacia atrás hasta 6 líneas el patrón NOMBRE (todo mayúsculas o capitalizado)
    ctx_back = [x for x in lines[max(0,i-8):i] if x and not EMAIL_RE.search(x) and not x.startswith(('Página','TECNICOS','NOMBRE','PRIMER','SEGUNDO','TLF','TITULACION','Nº','lunes','No estar','cumplan','energética','Esta base','Este listado'))]
    ctx_fwd = [x for x in lines[i+1:i+6] if x and not EMAIL_RE.search(x) and not x.startswith(('Página','TECNICOS','NOMBRE','PRIMER','SEGUNDO','TLF','TITULACION','Nº','lunes','No estar','cumplan','energética','Esta base','Este listado'))]
    records.append({'email': email.lower(), 'antes': ' | '.join(ctx_back[-5:]), 'despues': ' | '.join(ctx_fwd[:3])})

print("Registros:", len(records))
with open('C:/Users/artur/certificadoya/scripts/asturias_records.json','w',encoding='utf-8') as f:
    import json
    json.dump(records, f, ensure_ascii=False, indent=1)
