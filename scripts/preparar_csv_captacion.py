#!/usr/bin/env python3
"""
Preparar CSV de técnicos CEE para campaña de captación:
1. Filtra placeholders
2. Clasifica: personal vs institucional
3. Deduplica por email (el primer dominio gana)
4. Detecta provincia
5. Guarda CSV listo para envío
"""
import csv, json, os, re

INPUT = os.path.expanduser('~/AppData/Local/hermes/scripts/tecnicos_patrones.csv')
OUTPUT = os.path.expanduser('~/AppData/Local/hermes/scripts/tecnicos_captacion.csv')
JSON_FILE = os.path.expanduser('~/AppData/Local/hermes/scripts/tecnicos_captacion.json')

PLACEHOLDERS = [
    'info@empresa.com', 'tu@email.com', 'tu_correo@email.com',
    'contacto@ejemplo.com', 'contact@payhip.com', '20info@',
    'john@doe', 'misterello', 'example', 'tudominio',
    'test@', 'demo@', 'youremail', 'your@',
    'colegio@', '@colegio'
]

INSTITUCIONAL_DOMS = [
    'coaat', 'coac.', 'coam', 'cscae', 'coavn', 'apatgn',
    'caat', 'entremuros', 'aparejadores', 'aparejador',
]

INSTITUCIONAL_KEYWORDS = ['info@', 'colegio@', 'administracion@',
                          'gabinete@', 'admon@', 'secretaria@',
                          'valencia@caat', 'denia@']

# Mapa ciudad-en-dominio → provincia legible
PROV_MAP = {
    'alava': 'Álava', 'albacete': 'Albacete', 'alicante': 'Alicante',
    'almeria': 'Almería', 'asturias': 'Asturias', 'avila': 'Ávila',
    'badajoz': 'Badajoz', 'barcelona': 'Barcelona', 'burgos': 'Burgos',
    'caceres': 'Cáceres', 'cadiz': 'Cádiz', 'cantabria': 'Cantabria',
    'castellon': 'Castellón', 'ciudadreal': 'Ciudad Real', 'cordoba': 'Córdoba',
    'coruna': 'A Coruña', 'cuenca': 'Cuenca', 'girona': 'Girona',
    'granada': 'Granada', 'guadalajara': 'Guadalajara', 'guipuzcoa': 'Guipúzcoa',
    'huelva': 'Huelva', 'huesca': 'Huesca', 'jaen': 'Jaén',
    'leon': 'León', 'lleida': 'Lleida', 'lugo': 'Lugo', 'madrid': 'Madrid',
    'malaga': 'Málaga', 'murcia': 'Murcia', 'navarra': 'Navarra',
    'ourense': 'Ourense', 'palencia': 'Palencia', 'palmas': 'Las Palmas',
    'pontevedra': 'Pontevedra', 'rioja': 'La Rioja', 'salamanca': 'Salamanca',
    'segovia': 'Segovia', 'sevilla': 'Sevilla', 'soria': 'Soria',
    'tarragona': 'Tarragona', 'tenerife': 'Santa Cruz de Tenerife',
    'teruel': 'Teruel', 'toledo': 'Toledo', 'valencia': 'Valencia',
    'valladolid': 'Valladolid', 'vizcaya': 'Vizcaya', 'zamora': 'Zamora',
    'zaragoza': 'Zaragoza',
}

def detectar_provincia(dominio):
    """Extraer provincia del dominio"""
    dom = dominio.lower()
    mejor = ('', '')
    for key, prov in PROV_MAP.items():
        if key in dom and len(key) > len(mejor[0]):
            mejor = (key, prov)
    return mejor[1]

def es_placeholder(email):
    e = email.lower()
    for p in PLACEHOLDERS:
        if p in e:
            return True
    return False

def es_institucional(email, dominio):
    e = email.lower()
    d = dominio.lower()
    for kw in INSTITUCIONAL_KEYWORDS:
        if kw in e:
            return True
    for dom in INSTITUCIONAL_DOMS:
        if dom in d:
            return True
    return False

def main():
    # Leer CSV
    emails_encontrados = {}  # email -> {dominio, provincia, tipo, cee}
    
    with open(INPUT, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip().lower()
            dominio = row.get('dominio', '').strip().lower()
            cee = row.get('cee', 'False') == 'True'
            
            if not email:
                continue
            if es_placeholder(email):
                continue
            if email.count('@') != 1:
                continue
            
            # Guardar solo el primer dominio que vimos para este email
            if email not in emails_encontrados:
                prov = detectar_provincia(dominio)
                inst = es_institucional(email, dominio)
                emails_encontrados[email] = {
                    'email': email,
                    'dominio': dominio,
                    'provincia': prov,
                    'tipo': 'institucional' if inst else 'personal',
                    'cee': cee,
                }
    
    # Clasificar y ordenar
    personales = [e for e in emails_encontrados.values() if e['tipo'] == 'personal']
    institucionales = [e for e in emails_encontrados.values() if e['tipo'] == 'institucional']
    
    # Guardar CSV
    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['email', 'dominio', 'provincia', 'tipo', 'cee'])
        w.writeheader()
        for e in personales + institucionales:
            w.writerow(e)
    
    # Guardar JSON
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump({'personales': personales, 'institucionales': institucionales},
                  f, ensure_ascii=False, indent=2)
    
    print(f"{'='*50}")
    print(f"CSV PREPARADO")
    print(f"{'='*50}")
    print(f"Total emails únicos: {len(emails_encontrados)}")
    print(f"  Personales: {len(personales)}")
    print(f"  Institucionales: {len(institucionales)}")
    print()
    
    print("📧 PERSONALES (para outreach directo):")
    for e in personales:
        print(f"  {e['email']:45s} | {e['provincia'] or '??':20s} | {e['dominio']}")
    
    print(f"\n🏛️  INSTITUCIONALES (colegios, para otro enfoque):")
    for e in institucionales:
        print(f"  {e['email']:45s} | {e['provincia'] or '??':20s}")
    
    print(f"\n📁 CSV: {OUTPUT}")
    print(f"   JSON: {JSON_FILE}")

if __name__ == '__main__':
    main()
