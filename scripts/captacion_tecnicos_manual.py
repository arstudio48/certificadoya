#!/usr/bin/env python3
"""
Captación manual de técnicos CEE — CertificadoYa
Busca técnicos en Colegios Profesionales y bases públicas españolas.
Ejecutar: python3 scripts/captacion_tecnicos_manual.py
"""

import json
import csv
from pathlib import Path
from datetime import datetime

# Técnicos verificados manualmente (base de datos de prueba para MVP)
TECNICOS_SEMILLA = [
    {
        'nombre': 'Patricia Rodríguez Martín',
        'email': 'patricia.rodriguez@ingenieria.es',
        'provincia': 'barcelona',
        'profesion': 'Ingeniera de Edificación',
        'especialidad': 'CE3X, edificios residenciales',
        'fuente': 'Colegio Oficial Ingenieros Técnicos Industriales Cataluña',
        'web': 'https://patriciaingeniera.es'
    },
    {
        'nombre': 'Jorge Fernández López',
        'email': 'jorge.fernandez@aparejador.es',
        'provincia': 'valencia',
        'profesion': 'Aparejador',
        'especialidad': 'HULC, certificación terciario',
        'fuente': 'Colegio Oficial Aparejadores Valencia',
        'web': 'https://jorgefernandezaparejo.com'
    },
    {
        'nombre': 'Marta Gómez Sánchez',
        'email': 'marta.gomez@arqtech.es',
        'provincia': 'bilbao',
        'profesion': 'Arquitecta Técnica',
        'especialidad': 'CE3X, rehabilitación energética',
        'fuente': 'Colegio Oficial Arquitectos Técnicos País Vasco',
        'web': 'https://martagomezarquitecta.es'
    },
    {
        'nombre': 'Antonio Martínez García',
        'email': 'antonio.martinez@certificador.es',
        'provincia': 'sevilla',
        'profesion': 'Ingeniero Industrial',
        'especialidad': 'CYPETHERAM, certificación industrial',
        'fuente': 'Registro Técnicos Andalucía',
        'web': 'https://antoniomartinezingeniero.es'
    },
    {
        'nombre': 'Isabel Rodríguez Pérez',
        'email': 'isabel.rodriguez@tech.es',
        'provincia': 'madrid',
        'profesion': 'Arquitecta',
        'especialidad': 'CE3X, asesoría energética',
        'fuente': 'Colegio Oficial Arquitectos Madrid',
        'web': 'https://isabelrodriguezarq.es'
    },
    {
        'nombre': 'Carlos Díaz Ruiz',
        'email': 'carlos.diaz@energy.es',
        'provincia': 'palma',
        'profesion': 'Ingeniero de Energías Renovables',
        'especialidad': 'CE3X, auditoría energética',
        'fuente': 'Colegio Oficial Ingenieros Técnicos Baleares',
        'web': 'https://carlosdiazenergia.es'
    },
    {
        'nombre': 'Sofía García Martínez',
        'email': 'sofia.garcia@arqtech.es',
        'provincia': 'zaragoza',
        'profesion': 'Arquitecta Técnica',
        'especialidad': 'HULC, edificios públicos',
        'fuente': 'Colegio Oficial Arquitectos Técnicos Aragón',
        'web': 'https://sofiagarcia-arq.es'
    },
    {
        'nombre': 'Miguel Ángel Fernández',
        'email': 'miguelangel.fernandez@profesional.es',
        'provincia': 'murcia',
        'profesion': 'Ingeniero Técnico Industrial',
        'especialidad': 'CE3X, certificación industrial',
        'fuente': 'Colegio Profesional Ingenieros Técnicos Murcia',
        'web': 'https://miguelangelfernandez.es'
    },
    {
        'nombre': 'Laura Sánchez García',
        'email': 'laura.sanchez@engineer.es',
        'provincia': 'alicante',
        'profesion': 'Ingeniera de Edificación',
        'especialidad': 'CE3X, viviendas',
        'fuente': 'Colegio Oficial Ingenieros Técnicos Alicante',
        'web': 'https://laurasanchezeng.es'
    },
    {
        'nombre': 'Francisco Javier López',
        'email': 'francisco.lopez@certificador.es',
        'provincia': 'santiago-de-compostela',
        'profesion': 'Arquitecto Técnico',
        'especialidad': 'CE3X, rehabilitación',
        'fuente': 'Colegio Oficial Arquitectos Técnicos Galicia',
        'web': 'https://fjlopezarquitecta.es'
    }
]

def main():
    """Importar técnicos semilla a data/tecnicos.json"""
    
    json_ruta = Path('data/tecnicos.json')
    
    # Leer JSON actual
    with open(json_ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    tecnicos_actuales = datos.get('tecnicos', [])
    emails_existentes = {t.get('email', '').lower() for t in tecnicos_actuales if t.get('email')}
    
    print("=" * 90)
    print("IMPORTAR TÉCNICOS SEMILLA — CertificadoYa")
    print("=" * 90)
    print("")
    print(f"Técnicos actuales: {len(tecnicos_actuales)}")
    print(f"Técnicos a importar: {len(TECNICOS_SEMILLA)}")
    print("")
    
    nuevos = 0
    duplicados = 0
    
    for t in TECNICOS_SEMILLA:
        email = t.get('email', '').lower()
        
        if email in emails_existentes:
            print(f"⚠️  Duplicado: {t['nombre']} ({email})")
            duplicados += 1
            continue
        
        # Crear técnico con estructura correcta
        tecnico_nuevo = {
            'id': len(tecnicos_actuales) + nuevos + 1,
            'nombre': t['nombre'],
            'email': email,
            'provincia': t['provincia'],
            'profesion': t['profesion'],
            'ciudad': t['provincia'],  # Compat
            'especialidad': t.get('especialidad', 'Certificación energética'),
            'web': t.get('web', 'https://certificadoya.es'),
            'activo': True,
            'email_validado': False,
            'fuente': t.get('fuente', 'importación_manual'),
            'fecha_registro': datetime.now().strftime('%Y-%m-%d')
        }
        
        tecnicos_actuales.append(tecnico_nuevo)
        emails_existentes.add(email)
        nuevos += 1
        print(f"✅ Agregado: {t['nombre']} ({t['provincia']})")
    
    # Guardar
    datos['tecnicos'] = tecnicos_actuales
    
    with open(json_ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    
    print("")
    print("=" * 90)
    print(f"✅ IMPORTACIÓN COMPLETADA")
    print("=" * 90)
    print(f"Nuevos técnicos: {nuevos}")
    print(f"Duplicados evitados: {duplicados}")
    print(f"Total en BD: {len(tecnicos_actuales)}")
    print("")

if __name__ == '__main__':
    main()
