#!/usr/bin/env python3
"""Generate 14 Madrid district landing pages."""

import os

BASE = '/home/arturo/certificadoya'
TEMPLATE_PATH = f'{BASE}/certificado-energetico-madrid/index.html'

with open(TEMPLATE_PATH) as f:
    template = f.read()

MADRID_DISTRICTS = [
    {"slug": "certificado-energetico-madrid-centro", "city": "Madrid Centro", "cp": "28012",
     "price": 69, "market_low": 69, "market_high": 140,
     "lead": "Centro (Sol, Ópera, Palacio, Embajadores, Justicia, Universidad)."},
    {"slug": "certificado-energetico-chamberi", "city": "Chamberí", "cp": "28003",
     "price": 65, "market_low": 65, "market_high": 130,
     "lead": "Chamberí (Almagro, Arapiles, Gaztambide, Ríos Rosas, Trafalgar, Vallehermoso)."},
    {"slug": "certificado-energetico-salamanca-madrid", "city": "Salamanca", "cp": "28001",
     "price": 75, "market_low": 75, "market_high": 150,
     "lead": "Barrio de Salamanca (Recoletos, Goya, Lista, Castellana, Fuente del Berro, Guindalera). Zona prime de Madrid."},
    {"slug": "certificado-energetico-retiro", "city": "Retiro", "cp": "28009",
     "price": 75, "market_low": 75, "market_high": 145,
     "lead": "Retiro (Pacífico, Adelfas, Estrella, Ibiza, Jerónimos, Niño Jesús)."},
    {"slug": "certificado-energetico-chamartin", "city": "Chamartín", "cp": "28002",
     "price": 70, "market_low": 70, "market_high": 135,
     "lead": "Chamartín (El Viso, Prosperidad, Ciudad Jardín, Hispanoamérica, Nueva España, Castilla)."},
    {"slug": "certificado-energetico-tetuan", "city": "Tetuán", "cp": "28020",
     "price": 60, "market_low": 60, "market_high": 100,
     "lead": "Tetuán (Bellas Vistas, Cuatro Caminos, Castillejos, Almenara, Valdeacederas, Berruguete)."},
    {"slug": "certificado-energetico-mostoles", "city": "Móstoles", "cp": "28931",
     "price": 55, "market_low": 55, "market_high": 95,
     "lead": "Móstoles, segunda ciudad más poblada de la Comunidad de Madrid."},
    {"slug": "certificado-energetico-getafe", "city": "Getafe", "cp": "28901",
     "price": 55, "market_low": 55, "market_high": 95,
     "lead": "Getafe, zona sur metropolitana con gran parque de viviendas."},
    {"slug": "certificado-energetico-leganes", "city": "Leganés", "cp": "28911",
     "price": 55, "market_low": 55, "market_high": 90,
     "lead": "Leganés, zona sur. Precios competitivos por alta densidad de técnicos."},
    {"slug": "certificado-energetico-alcala-de-henares", "city": "Alcalá de Henares", "cp": "28801",
     "price": 55, "market_low": 55, "market_high": 95,
     "lead": "Alcalá de Henares, Patrimonio de la Humanidad y corredor del Henares."},
    {"slug": "certificado-energetico-alcorcon", "city": "Alcorcón", "cp": "28921",
     "price": 55, "market_low": 55, "market_high": 90,
     "lead": "Alcorcón, zona suroeste metropolitana."},
    {"slug": "certificado-energetico-fuenlabrada", "city": "Fuenlabrada", "cp": "28941",
     "price": 50, "market_low": 50, "market_high": 85,
     "lead": "Fuenlabrada, el precio más competitivo de la Comunidad de Madrid."},
    {"slug": "certificado-energetico-pozuelo", "city": "Pozuelo de Alarcón", "cp": "28223",
     "price": 75, "market_low": 75, "market_high": 150,
     "lead": "Pozuelo de Alarcón, zona noroeste premium con viviendas unifamiliares."},
    {"slug": "certificado-energetico-alcobendas", "city": "Alcobendas", "cp": "28100",
     "price": 65, "market_low": 65, "market_high": 120,
     "lead": "Alcobendas, zona norte empresarial y residencial."},
]

def make_district_page(data):
    c = data["city"]
    slug = data["slug"]
    cp = data["cp"]
    price = data["price"]
    lead = data["lead"]
    market_low = data.get("market_low", price)
    market_high = data.get("market_high", price * 2)

    page = template

    # Title
    page = page.replace(
        "<title>Certificado Energético en Madrid — Presupuesto en 24h | Desde 60€</title>",
        f"<title>Certificado Energético en {c} — Presupuesto en 24h | Desde {price}€</title>"
    )
    # Description
    page = page.replace(
        '<meta name="description" content="Certificado de eficiencia energética (CEE) en Madrid. Presupuesto instantáneo por m². Técnicos verificados en Madrid capital y comunidad. Desde 60€. Entrega en 24-48h.">',
        f'<meta name="description" content="Certificado de eficiencia energética (CEE) en {c}. Presupuesto instantáneo por m². Técnicos verificados en {c}. Desde {price}€. Entrega en 24-48h.">'
    )
    # Keywords
    page = page.replace(
        '<meta name="keywords" content="certificado energético Madrid, CEE Madrid, precio certificado energético Madrid, técnico certificador Madrid">',
        f'<meta name="keywords" content="certificado energético {c}, CEE {c}, precio certificado energético {c}, técnico certificador {c}">'
    )
    # Canonical
    page = page.replace(
        '<link rel="canonical" href="https://www.certificadoya.es/certificado-energetico-madrid">',
        f'<link rel="canonical" href="https://www.certificadoya.es/{slug}">'
    )
    # OG title
    page = page.replace(
        '<meta property="og:title" content="Certificado Energético en Madrid — Presupuesto en 24h | Desde 60€">',
        f'<meta property="og:title" content="Certificado Energético en {c} — Presupuesto en 24h | Desde {price}€">'
    )
    # OG desc
    page = page.replace(
        '<meta property="og:description" content="Presupuesto instantáneo para tu certificado energético en Madrid. Técnicos verificados en Madrid capital y comunidad. Desde 60-96€ para un piso estándar.">',
        f'<meta property="og:description" content="Presupuesto instantáneo para tu certificado energético en {c}. Técnicos verificados. Desde {market_low}-{market_high}€ para un piso estándar.">'
    )
    # OG URL
    page = page.replace(
        '<meta property="og:url" content="https://www.certificadoya.es/certificado-energetico-madrid">',
        f'<meta property="og:url" content="https://www.certificadoya.es/{slug}">'
    )
    # Twitter
    page = page.replace(
        '<meta name="twitter:title" content="Certificado Energético en Madrid — Desde 60€">',
        f'<meta name="twitter:title" content="Certificado Energético en {c} — Desde {price}€">'
    )
    page = page.replace(
        '<meta name="twitter:description" content="Técnicos verificados en Madrid capital y comunidad. Presupuesto al instante.">',
        f'<meta name="twitter:description" content="Técnicos verificados en {c}. Presupuesto al instante.">'
    )

    # Schema LocalBusiness
    page = page.replace(
        '"name": "CertificadoYa — Certificado Energético en Madrid"',
        f'"name": "CertificadoYa — Certificado Energético en {c}"'
    )
    page = page.replace(
        '"description": "Certificados de eficiencia energética (CEE) en Madrid. Técnicos verificados. Presupuesto instantáneo."',
        f'"description": "Certificados de eficiencia energética (CEE) en {c}. Técnicos verificados. Presupuesto instantáneo."'
    )
    page = page.replace(
        '"url": "https://www.certificadoya.es/certificado-energetico-madrid"',
        f'"url": "https://www.certificadoya.es/{slug}"'
    )
    page = page.replace(
        '"name": "Madrid"',
        f'"name": "{c}"'
    )
    page = page.replace(
        '"addressLocality": "Madrid"',
        f'"addressLocality": "{c}"'
    )
    page = page.replace(
        '"name": "Certificado Energético (CEE) en Madrid"',
        f'"name": "Certificado Energético (CEE) en {c}"'
    )
    page = page.replace(
        '"description": "Emisión y registro del CEE por técnico colegiado en Madrid capital y comunidad"',
        f'"description": "Emisión y registro del CEE por técnico colegiado en {c}"'
    )
    page = page.replace(
        '"price": 60,',
        f'"price": {price},'
    )
    page = page.replace(
        '"minPrice": 60',
        f'"minPrice": {price}'
    )
    # Breadcrumb Schema
    page = page.replace(
        '"name": "Certificado energético en Madrid"',
        f'"name": "Certificado energético en {c}"'
    )

    # Body: Breadcrumb
    page = page.replace(
        '› Certificado energético en Madrid',
        f'› Certificado energético en {c}'
    )

    # H1
    page = page.replace(
        '<h1>Certificado energético <span>en Madrid</span></h1>',
        f'<h1>Certificado energético <span>en {c}</span></h1>'
    )
    # Lead
    page = page.replace(
        '<p class="lead">Presupuesto al instante para tu certificado de eficiencia energética (CEE) en Madrid capital y comunidad. Técnicos colegiados verificados. Resultado en 24-48 horas.</p>',
        f'<p class="lead">Presupuesto al instante para tu certificado de eficiencia energética (CEE) en {c}. Técnicos colegiados verificados. {lead}. Resultado en 24-48 horas.</p>'
    )

    # Calculator
    page = page.replace('en Madrid</h3>', f'en {c}</h3>')
    page = page.replace('placeholder="Ej: 28001"', f'placeholder="Ej: {cp}"')

    # Content section
    page = page.replace(
        '<h2>Certificado energético en Madrid: rápido, fácil y al mejor precio</h2>',
        f'<h2>Certificado energético en {c}: rápido, fácil y al mejor precio</h2>'
    )
    page = page.replace(
        '<strong>Madrid capital y comunidad</strong>',
        f'<strong>{c}</strong>'
    )
    page = page.replace(
        '<strong>60€</strong> para un piso estándar',
        f'<strong>{price}€</strong> para un piso estándar'
    )

    # Pricing grid
    p1 = price
    p2 = max(price, int(price * 1.3))
    p3 = int(price * 1.55)
    p4 = max(price, 75)
    page = page.replace('60-96€', f'{p1}-{p2}€', 1)  # first occurrence = piso 50-70
    page = page.replace('<span>Desde 96€</span>', f'<span>Desde {p2}€</span>')
    page = page.replace('<span>121-156€</span>', f'<span>{p3}-{int(p3*1.3)}€</span>')
    page = page.replace('<span>Desde 75€</span>', f'<span>Desde {p4}€</span>')

    # Why choose us
    page = page.replace('en Madrid?</h3>', f'en {c}?</h3>')
    page = page.replace(
        '<li><strong>Técnicos colegiados en Madrid</strong>: arquitectos, aparejadores e ingenieros verificados</li>',
        f'<li><strong>Técnicos colegiados en {c}</strong>: arquitectos, aparejadores e ingenieros verificados</li>'
    )

    # FAQ
    page = page.replace(
        'Preguntas frecuentes sobre el CEE en Madrid</h3>',
        f'Preguntas frecuentes sobre el CEE en {c}</h3>'
    )
    page = page.replace(
        '¿Cuánto cuesta un certificado energético en Madrid?</summary>',
        f'¿Cuánto cuesta un certificado energético en {c}?</summary>'
    )
    page = page.replace(
        '<p>El precio de un certificado energético en Madrid oscila entre <strong>60-96€</strong> para un piso de 60-80 m².',
        f'<p>El precio de un certificado energético en {c} oscila entre <strong>{market_low}-{market_high}€</strong> para un piso de 60-80 m².'
    )
    page = page.replace(
        '¿En cuánto tiempo tengo el certificado en Madrid?</summary>',
        f'¿En cuánto tiempo tengo el certificado en {c}?</summary>'
    )
    page = page.replace(
        'a tu domicilio en Madrid capital y comunidad',
        f'a tu domicilio en {c}'
    )

    # CTA band
    page = page.replace(
        '¿Necesitas tu certificado energético en Madrid?</p>',
        f'¿Necesitas tu certificado energético en {c}?</p>'
    )

    # CTA técnicos
    page = page.replace(
        'Recibe clientes en tu zona',
        f'Recibe clientes en {c}'
    )
    page = page.replace(
        "'+ nombre + '! Un técnico en Madrid te contactará",
        f"'+ nombre + '! Un técnico en {c} te contactará"
    )
    page = page.replace(
        "localidad: 'Madrid',",
        f"localidad: '{c}',"
    )
    page = page.replace(
        "cp.value || '28001'",
        f"cp.value || '{cp}'"
    )
    page = page.replace(
        "params.get('cp') || '28001'",
        f"params.get('cp') || '{cp}'"
    )

    os.makedirs(f'{BASE}/{slug}', exist_ok=True)
    with open(f'{BASE}/{slug}/index.html', 'w') as f:
        f.write(page)
    return slug


# ── Run ──
print("🏗️  Generando 14 landings de distritos Madrid...")
for d in MADRID_DISTRICTS:
    slug = make_district_page(d)
    print(f"  ✅ {slug} (desde {d['price']}€)")

print(f"\n🎉 ¡{len(MADRID_DISTRICTS)} páginas generadas!")
