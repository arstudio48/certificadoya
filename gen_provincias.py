import os, re

# Provincias que faltan (las que están en el selector pero no tienen página)
nuevas = {
    'alava': {'nombre': 'Álava', 'cp_ejemplo': '01001', 'precio': (0.45, 0.85)},
    'albacete': {'nombre': 'Albacete', 'cp_ejemplo': '02001', 'precio': (0.45, 0.85)},
    'almeria': {'nombre': 'Almería', 'cp_ejemplo': '04001', 'precio': (0.45, 0.85)},
    'avila': {'nombre': 'Ávila', 'cp_ejemplo': '05001', 'precio': (0.45, 0.85)},
    'burgos': {'nombre': 'Burgos', 'cp_ejemplo': '09001', 'precio': (0.45, 0.85)},
    'castellon': {'nombre': 'Castellón', 'cp_ejemplo': '12001', 'precio': (0.50, 0.85)},
    'ceuta': {'nombre': 'Ceuta', 'cp_ejemplo': '51001', 'precio': (0.50, 0.85)},
    'ciudad-real': {'nombre': 'Ciudad Real', 'cp_ejemplo': '13001', 'precio': (0.45, 0.80)},
    'cordoba': {'nombre': 'Córdoba', 'cp_ejemplo': '14001', 'precio': (0.45, 0.80)},
    'cuenca': {'nombre': 'Cuenca', 'cp_ejemplo': '16001', 'precio': (0.45, 0.80)},
    'girona': {'nombre': 'Girona', 'cp_ejemplo': '17001', 'precio': (0.50, 0.85)},
    'guadalajara': {'nombre': 'Guadalajara', 'cp_ejemplo': '19001', 'precio': (0.45, 0.80)},
    'huelva': {'nombre': 'Huelva', 'cp_ejemplo': '21001', 'precio': (0.45, 0.80)},
    'huesca': {'nombre': 'Huesca', 'cp_ejemplo': '22001', 'precio': (0.45, 0.80)},
    'jaen': {'nombre': 'Jaén', 'cp_ejemplo': '23001', 'precio': (0.45, 0.80)},
    'lleida': {'nombre': 'Lleida', 'cp_ejemplo': '25001', 'precio': (0.50, 0.85)},
    'lugo': {'nombre': 'Lugo', 'cp_ejemplo': '27001', 'precio': (0.45, 0.80)},
    'melilla': {'nombre': 'Melilla', 'cp_ejemplo': '52001', 'precio': (0.50, 0.85)},
    'navarra': {'nombre': 'Navarra', 'cp_ejemplo': '31001', 'precio': (0.50, 0.85)},
    'ourense': {'nombre': 'Ourense', 'cp_ejemplo': '32001', 'precio': (0.45, 0.80)},
    'palencia': {'nombre': 'Palencia', 'cp_ejemplo': '34001', 'precio': (0.45, 0.80)},
    'pontevedra': {'nombre': 'Pontevedra', 'cp_ejemplo': '36001', 'precio': (0.45, 0.80)},
    'segovia': {'nombre': 'Segovia', 'cp_ejemplo': '40001', 'precio': (0.45, 0.80)},
    'soria': {'nombre': 'Soria', 'cp_ejemplo': '42001', 'precio': (0.45, 0.80)},
    'tarragona': {'nombre': 'Tarragona', 'cp_ejemplo': '43001', 'precio': (0.50, 0.85)},
    'teruel': {'nombre': 'Teruel', 'cp_ejemplo': '44001', 'precio': (0.45, 0.80)},
    'toledo': {'nombre': 'Toledo', 'cp_ejemplo': '45001', 'precio': (0.45, 0.80)},
    'zamora': {'nombre': 'Zamora', 'cp_ejemplo': '49001', 'precio': (0.45, 0.80)},
}

# Leer Madrid como plantilla
with open('/tmp/certificadoya/certificado-energetico-madrid/index.html', 'r') as f:
    plantilla = f.read()

for slug, info in nuevas.items():
    nombre = info['nombre']
    cp_ej = info['cp_ejemplo']
    
    content = plantilla
    
    # Reemplazar título y meta
    content = content.replace(
        'Certificado Energético en Madrid — Presupuesto en 24h | Desde 60€',
        f'Certificado Energético en {nombre} — Presupuesto en 24h | Desde 45€'
    )
    content = content.replace(
        'Certificado de eficiencia energética (CEE) en Madrid. Presupuesto instantáneo por m². Técnicos verificados en Madrid capital y comunidad. Desde 60€. Entrega en 24-48h.',
        f'Certificado de eficiencia energética (CEE) en {nombre}. Presupuesto instantáneo por m². Técnicos verificados en {nombre}. Desde 45€. Entrega en 24-48h.'
    )
    content = content.replace(
        'certificado energético Madrid, CEE Madrid, precio certificado energético Madrid, técnico certificador Madrid',
        f'certificado energético {nombre.lower()}, CEE {nombre.lower()}, precio certificado energético {nombre.lower()}, técnico certificador {nombre.lower()}'
    )
    content = content.replace(
        '/certificado-energetico-madrid',
        f'/certificado-energetico-{slug}'
    )
    
    # Reemplazar texto "en Madrid" por "en {nombre}"
    content = content.replace('en Madrid', f'en {nombre}')
    content = content.replace('en Madrid capital y comunidad', f'en {nombre}')
    content = content.replace('Madrid capital y comunidad', nombre)
    content = content.replace('Madrid capital', nombre)
    
    # Reemplazar precio base (60-96 a 45-85)
    content = content.replace('60€', '45€')
    content = content.replace('60-96€', '45-80€')
    content = content.replace('96€', '80€')
    content = content.replace('Desde 96€', 'Desde 80€')
    content = content.replace('Desde 60€', 'Desde 45€')
    content = content.replace('Desde 60', 'Desde 45')
    
    # Precio orientativo
    content = content.replace('Piso 50-70 m²</strong><span>60-96€', f'Piso 50-70 m²</strong><span>45-80€')
    content = content.replace('Piso 70-100 m²</strong><span>Desde 96€', f'Piso 70-100 m²</strong><span>Desde 80€')
    
    # FAQ - reemplazar referencias Madrid
    content = content.replace('piso de 60-80 m² en Madrid: 60-96 €', f'piso de 60-80 m² en {nombre}: 45-80 €')
    content = content.replace('en Madrid capital y comunidad', f'en {nombre}')
    content = content.replace('en Madrid', f'en {nombre}')
    
    # Reemplazar en Schema LocalBusiness
    content = content.replace(
        '"name": "CertificadoYa — Certificado Energético en Madrid"',
        f'"name": "CertificadoYa — Certificado Energético en {nombre}"'
    )
    content = content.replace('"addressLocality": "Madrid"', f'"addressLocality": "{nombre}"')
    content = content.replace(
        '"name": "Certificado Energético (CEE) en Madrid"',
        f'"name": "Certificado Energético (CEE) en {nombre}"'
    )
    content = content.replace(
        '"description": "Emisión y registro del CEE por técnico colegiado en Madrid capital y comunidad"',
        f'"description": "Emisión y registro del CEE por técnico colegiado en {nombre}"'
    )
    
    # Reemplazar en BreadcrumbList
    content = content.replace(
        '"name": "Certificado energético en Madrid"',
        f'"name": "Certificado energético en {nombre}"'
    )
    
    # Título H1
    content = content.replace(
        '<h1>Certificado energético <span>en Madrid</span></h1>',
        f'<h1>Certificado energético <span>en {nombre}</span></h1>'
    )
    
    # Lead texto
    content = content.replace(
        'para tu certificado de eficiencia energética (CEE) en Madrid capital y comunidad.',
        f'para tu certificado de eficiencia energética (CEE) en {nombre}.'
    )
    content = content.replace('Técnicos colegiados verificados.', 'Técnicos colegiados verificados.')
    
    # Reemplazar "Madrid" en precios inline (para calcularPresupuesto)
    content = content.replace("'Madrid'", f"'{nombre}'")
    content = content.replace("'28001'", f"'{cp_ej}'")
    
    # Reemplazar breadcrumb
    content = content.replace('Certificado energético en Madrid', f'Certificado energético en {nombre}')
    content = content.replace('Madrid</a>', f'{nombre}</a>')
    
    # Reemplazar en el texto del H2
    content = content.replace(
        '<h2>Certificado energético en Madrid: rápido, fácil y al mejor precio</h2>',
        f'<h2>Certificado energético en {nombre}: rápido, fácil y al mejor precio</h2>'
    )
    
    # Reemplazar en las secciones de contenido
    content = content.replace(
        'certificado de eficiencia energética (CEE) para vender o alquilar tu vivienda en Madrid capital y comunidad',
        f'certificado de eficiencia energética (CEE) para vender o alquilar tu vivienda en {nombre}'
    )
    
    # Precios orientativos header
    content = content.replace(
        '<h3>💰 Precios orientativos en Madrid</h3>',
        f'<h3>💰 Precios orientativos en {nombre}</h3>'
    )
    
    # h3 ¿Por qué elegirnos en Madrid?
    content = content.replace(
        '<h3>✅ ¿Por qué elegirnos en Madrid?</h3>',
        f'<h3>✅ ¿Por qué elegirnos en {nombre}?</h3>'
    )
    
    # Técnicos colegiados en Madrid
    content = content.replace(
        'Técnicos colegiados en Madrid',
        f'Técnicos colegiados en {nombre}'
    )
    
    # FAQ
    content = content.replace(
        '<h3>📍 Preguntas frecuentes sobre el CEE en Madrid</h3>',
        f'<h3>📍 Preguntas frecuentes sobre el CEE en {nombre}</h3>'
    )
    content = content.replace(
        '¿Cuánto cuesta un certificado energético en Madrid?',
        f'¿Cuánto cuesta un certificado energético en {nombre}?'
    )
    content = content.replace(
        'un certificado energético en Madrid oscila',
        f'un certificado energético en {nombre} oscila'
    )
    content = content.replace(
        '¿En cuánto tiempo tengo el certificado en Madrid?',
        f'¿En cuánto tiempo tengo el certificado en {nombre}?'
    )
    content = content.replace(
        'El proceso completo dura <strong>48-72 horas</strong>: 24-48h para la visita del técnico a tu domicilio en Madrid capital y comunidad',
        f'El proceso completo dura <strong>48-72 horas</strong>: 24-48h para la visita del técnico a tu domicilio en {nombre}'
    )
    content = content.replace(
        '¿Es obligatorio el certificado energético en Madrid?',
        f'¿Es obligatorio el certificado energético en {nombre}?'
    )
    content = content.replace(
        'también en Madrid',
        f'también en {nombre}'
    )
    
    # CTA band
    content = content.replace(
        '¿Necesitas tu certificado energético en Madrid?',
        f'¿Necesitas tu certificado energético en {nombre}?'
    )
    
    # canonical URL
    content = content.replace(
        'href="https://www.certificadoya.es/certificado-energetico-madrid"',
        f'href="https://www.certificadoya.es/certificado-energetico-{slug}"'
    )
    
    # OG tags
    content = content.replace(
        'Certificado Energético en Madrid — Presupuesto en 24h | Desde 60€',
        f'Certificado Energético en {nombre} — Presupuesto en 24h | Desde 45€'
    )
    content = content.replace(
        'Presupuesto instantáneo para tu certificado energético en Madrid. Técnicos verificados en Madrid capital y comunidad. Desde 60-96€ para un piso estándar.',
        f'Presupuesto instantáneo para tu certificado energético en {nombre}. Técnicos verificados en {nombre}. Desde 45€ para un piso estándar.'
    )
    content = content.replace(
        'Técnicos verificados en Madrid capital y comunidad. Presupuesto al instante.',
        f'Técnicos verificados en {nombre}. Presupuesto al instante.'
    )
    
    # Crear directorio y escribir
    outdir = f'/tmp/certificadoya/certificado-energetico-{slug}'
    os.makedirs(outdir, exist_ok=True)
    with open(f'{outdir}/index.html', 'w') as f:
        f.write(content)
    print(f"✅ {slug} ({nombre})")

print(f"\nGeneradas {len(nuevas)} páginas de provincia")
