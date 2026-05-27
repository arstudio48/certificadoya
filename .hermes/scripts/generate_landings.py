#!/usr/bin/env python3
"""Generate all missing SEO landing pages for CertificadoYa."""

import os
import re

BASE = '/home/arturo/certificadoya'
TEMPLATE_PATH = f'{BASE}/certificado-energetico-madrid/index.html'

with open(TEMPLATE_PATH) as f:
    template = f.read()

# ── Data definitions ──────────────────────────────────────────────

# Asturias cities
ASTURIAS_CITIES = [
    {"slug": "certificado-energetico-gijon", "city": "Gijón", "cp": "33201",
     "price": 55, "market_low": 55, "market_high": 110,
     "lead_text": "Gijón capital y zona metropolitana."},
    {"slug": "certificado-energetico-oviedo", "city": "Oviedo", "cp": "33001",
     "price": 59, "market_low": 59, "market_high": 120,
     "lead_text": "Oviedo capital y alrededores."},
    {"slug": "certificado-energetico-aviles", "city": "Avilés", "cp": "33401",
     "price": 50, "market_low": 50, "market_high": 95,
     "lead_text": "Avilés y comarca."},
    {"slug": "certificado-energetico-siero", "city": "Siero (Pola de Siero)", "cp": "33510",
     "price": 50, "market_low": 55, "market_high": 100,
     "lead_text": "Siero, Pola de Siero y alrededores."},
    {"slug": "certificado-energetico-langreo", "city": "Langreo", "cp": "33900",
     "price": 48, "market_low": 50, "market_high": 90,
     "lead_text": "Langreo y cuenca del Nalón."},
    {"slug": "certificado-energetico-mieres", "city": "Mieres", "cp": "33600",
     "price": 48, "market_low": 50, "market_high": 90,
     "lead_text": "Mieres y cuenca del Caudal."},
]

# Asturias transaccionales
AST_TRANS = [
    {"slug": "certificado-energetico-precio-asturias", "title": "Precio del Certificado Energético en Asturias — Desde 48€ | Presupuesto al Instante",
     "desc": "Descubre el precio real del certificado energético en Asturias. Compara precios por ciudad (Gijón, Oviedo, Avilés…). Desde 48€. Presupuesto instantáneo.",
     "h1": "Precio del certificado energético <span>en Asturias</span>",
     "lead": "Compara precios reales del certificado de eficiencia energética (CEE) en Asturias. En Gijón y Oviedo desde 55-59€, en las cuencas mineras desde 48€. Todo incluido, sin sorpresas.",
     "city": "Asturias", "cp": "33001", "price": 48, "zone": "Asturias",
     "provincia": "Asturias", "keyword": "precio certificado energético Asturias",
     "tasa_org": "Dirección General de Energía, Minería y Reactivación",
     "tasa_url": "https://sede.asturias.es/",
     "faq": [
         ("¿Cuánto cuesta un certificado energético en Asturias?", "El precio varía según la ciudad y el tamaño del inmueble. En <strong>Gijón desde 55€</strong>, en <strong>Oviedo desde 59€</strong>, en Avilés desde 50€, y en Langreo y Mieres desde 48€ para un piso estándar. Las viviendas unifamiliares son algo más caras."),
         ("¿Por qué hay diferencias de precio entre ciudades asturianas?", "La demanda de técnicos certificadores es mayor en Oviedo y Gijón, lo que eleva ligeramente los precios. En las cuencas mineras (Langreo, Mieres) hay más disponibilidad y los precios son más bajos."),
         ("¿El precio incluye el registro oficial?", "Sí, nuestro precio incluye la visita técnica, el cálculo con software oficial (CE3X), la emisión del certificado y el registro telemático en el Principado de Asturias."),
         ("¿Hay descuentos por varias viviendas?", "Sí. Si necesitas certificar varios inmuebles (por ejemplo, un edificio completo), contacta con nosotros y te ofrecemos un presupuesto personalizado con descuento por volumen."),
         ("¿Cómo se compara con la competencia en Asturias?", "CertiEnergy cobra desde 69€, TecniEco 79-99€, EnergyCert Asturias desde 59€. En CertificadoYa empezamos desde 48€ con el mismo servicio profesional."),
     ]},
    {"slug": "certificado-energetico-urgente-asturias", "title": "Certificado Energético Urgente en Asturias — 24h | Desde 48€",
     "desc": "Certificado energético urgente en Asturias (Gijón, Oviedo, Avilés, Langreo, Mieres). Entrega en 24 horas. Técnicos verificados. Presupuesto al instante. Desde 48€.",
     "h1": "Certificado energético urgente <span>en Asturias</span>",
     "lead": "¿Necesitas el certificado de eficiencia energética con urgencia en Asturias? Te lo entregamos en <strong>24 horas</strong> con técnicos verificados en Gijón, Oviedo, Avilés y toda la comunidad. Presupuesto instantáneo.",
     "city": "Asturias", "cp": "33001", "price": 48, "zone": "Asturias",
     "provincia": "Asturias", "keyword": "certificado energético urgente Asturias",
     "tasa_org": "Dirección General de Energía, Minería y Reactivación",
     "tasa_url": "https://sede.asturias.es/",
     "faq": [
         ("¿En cuánto tiempo tengo el certificado urgente en Asturias?", "En <strong>24 horas</strong> desde la solicitud. El técnico acude a tu domicilio el mismo día o al siguiente, y en 24h adicionales el certificado está emitido y registrado."),
         ("¿El servicio urgente tiene recargo?", "Sí, el servicio urgente tiene un pequeño recargo sobre la tarifa estándar. Te damos el precio exacto en el presupuesto instantáneo."),
         ("¿Cubrís todo Asturias en urgente?", "Sí, cubrimos <strong>Gijón, Oviedo, Avilés, Siero, Langreo, Mieres</strong> y toda Asturias con el servicio urgente."),
         ("¿Qué documentos necesito para el urgente?", "DNI/NIE del propietario, escritura o nota simple del inmueble. Si no tienes la nota simple, podemos ayudarte a conseguirla rápido."),
         ("¿Es legal un certificado emitido en 24h?", "Totalmente. El certificado lo firma un técnico colegiado y se registra telemáticamente en el Principado de Asturias, igual que uno que tarde una semana. La única diferencia es la velocidad."),
     ]},
    {"slug": "certificado-energetico-alquiler-asturias", "title": "Certificado Energético para Alquilar en Asturias — Obligatorio | Desde 48€",
     "desc": "Certificado energético obligatorio para alquilar vivienda en Asturias. Gijón, Oviedo, Avilés y toda la comunidad. Desde 48€. Evita multas de hasta 6.000€.",
     "h1": "Certificado energético para alquilar <span>en Asturias</span>",
     "lead": "Si vas a <strong>alquilar tu vivienda en Asturias</strong>, necesitas el certificado de eficiencia energética por ley. Te lo gestionamos rápido — desde 48€ en Langreo y Mieres, desde 55€ en Gijón.",
     "city": "Asturias", "cp": "33001", "price": 48, "zone": "Asturias",
     "provincia": "Asturias", "keyword": "certificado energético alquiler Asturias",
     "tasa_org": "Dirección General de Energía, Minería y Reactivación",
     "tasa_url": "https://sede.asturias.es/",
     "faq": [
         ("¿Es obligatorio el certificado energético para alquilar en Asturias?", "Sí, desde el 1 de junio de 2013 es <strong>obligatorio</strong> para todos los contratos de alquiler. La multa por no tenerlo puede llegar a <strong>6.000€</strong>."),
         ("¿Cuánto cuesta para un piso de alquiler en Asturias?", "Desde <strong>48€</strong> en Langreo y Mieres, desde <strong>55€</strong> en Gijón, y desde <strong>59€</strong> en Oviedo para un piso estándar."),
         ("¿Quién paga el certificado, el casero o el inquilino?", "El <strong>propietario/casero</strong> es el responsable legal de obtener y mostrar el certificado energético."),
         ("¿El inquilino puede pedir ver el certificado?", "Sí, el inquilino tiene derecho a ver la etiqueta de eficiencia energética antes de firmar el contrato."),
         ("¿Cada cuánto tengo que renovarlo para alquiler?", "El certificado tiene una validez de <strong>10 años</strong>. Pasado ese tiempo, hay que renovarlo."),
     ]},
    {"slug": "certificado-energetico-venta-vivienda-asturias", "title": "Certificado Energético para Vender Piso en Asturias | Desde 48€",
     "desc": "Vende tu piso en Asturias con el certificado energético obligatorio. Gijón, Oviedo, Avilés… Desde 48€. Técnicos verificados. Presupuesto instantáneo.",
     "h1": "Certificado energético para vender tu piso <span>en Asturias</span>",
     "lead": "Si estás vendiendo tu vivienda en Asturias, necesitas el certificado de eficiencia energética (CEE). Es obligatorio por ley y te lo gestionamos desde <strong>48€</strong>, con técnicos verificados en toda la comunidad.",
     "city": "Asturias", "cp": "33001", "price": 48, "zone": "Asturias",
     "provincia": "Asturias", "keyword": "certificado energético vender piso Asturias",
     "tasa_org": "Dirección General de Energía, Minería y Reactivación",
     "tasa_url": "https://sede.asturias.es/",
     "faq": [
         ("¿Necesito el certificado para vender mi piso en Asturias?", "Sí, es <strong>obligatorio</strong> por ley. No puedes formalizar la compraventa sin él. El notario te lo exigirá."),
         ("¿Cuánto cuesta para un piso en venta en Asturias?", "Desde <strong>48€</strong> en las cuencas mineras, <strong>55€</strong> en Gijón y <strong>59€</strong> en Oviedo para un piso estándar."),
         ("¿Afecta la letra energética al precio de venta?", "Sí. Una buena calificación (A, B o C) puede aumentar el valor de la vivienda entre un 5% y un 20% en el mercado asturiano."),
         ("¿Cuánto tarda en emitirse?", "48-72 horas desde la visita del técnico, o <strong>24h en servicio urgente</strong>."),
         ("¿Qué pasa si vendo sin certificado?", "La multa puede ser de hasta <strong>6.000€</strong> y la compraventa no puede formalizarse ante notario."),
     ]},
    {"slug": "multa-no-tener-certificado-energetico-asturias", "title": "Multa por No Tener Certificado Energético en Asturias — Hasta 6.000€ | Evítala",
     "desc": "Multas de hasta 6.000€ por no tener el certificado energético en Asturias. Infórmate de la normativa y consigue tu CEE desde 48€. Evita sanciones.",
     "h1": "Multa por no tener certificado energético <span>en Asturias</span>",
     "lead": "No tener el certificado de eficiencia energética en Asturias puede costarte hasta <strong>6.000€</strong> de multa. Infórmate de la normativa y ponte al día desde solo <strong>48€</strong>.",
     "city": "Asturias", "cp": "33001", "price": 48, "zone": "Asturias",
     "provincia": "Asturias", "keyword": "multa no tener certificado energético Asturias",
     "tasa_org": "Dirección General de Energía, Minería y Reactivación",
     "tasa_url": "https://sede.asturias.es/",
     "faq": [
         ("¿De cuánto es la multa por no tener el CEE en Asturias?", "Las sanciones pueden ir desde <strong>300€ hasta 6.000€</strong> según la gravedad. Las infracciones graves (no tenerlo en una compraventa) están en la franja alta."),
         ("¿Quién me puede multar?", "La <strong>Dirección General de Energía, Minería y Reactivación del Principado</strong> es el organismo competente. También puede detectarse en una inspección o al formalizar la compraventa ante notario."),
         ("¿Cómo evito la multa?", "Solicitando tu certificado energético antes de vender o alquilar. En CertificadoYa te lo gestionamos desde <strong>48€</strong>."),
         ("¿El certificado tiene fecha de caducidad?", "Sí, <strong>10 años</strong>. Después hay que renovarlo."),
         ("¿Puedo vender o alquilar sin él si el comprador acepta?", "No. El notario no puede formalizar la operación sin la etiqueta energética. No es negociable."),
     ]},
]

# Madrid transaccionales
MAD_TRANS = [
    {"slug": "certificado-energetico-urgente-madrid", "title": "Certificado Energético Urgente en Madrid — 24h | Desde 60€",
     "desc": "Certificado energético urgente en Madrid. Entrega en 24 horas. Técnicos verificados en Madrid capital y comunidad. Presupuesto instantáneo. Desde 60€.",
     "h1": "Certificado energético urgente <span>en Madrid</span>",
     "lead": "¿Necesitas el certificado de eficiencia energética con urgencia en Madrid? Te lo entregamos en <strong>24 horas</strong> con técnicos verificados en Madrid capital y comunidad. Presupuesto instantáneo.",
     "city": "Madrid", "cp": "28001", "price": 60, "zone": "Madrid",
     "provincia": "Madrid", "keyword": "certificado energético urgente Madrid",
     "tasa_org": "Dirección General de Industria, Energía y Minas",
     "tasa_url": "https://www.comunidad.madrid/servicios/energia/",
     "faq": [
         ("¿En cuánto tiempo tengo el certificado urgente?", "En <strong>24 horas</strong> desde la solicitud. El técnico acude a tu domicilio en Madrid el mismo día, y en 24h el certificado está emitido y registrado."),
         ("¿El servicio urgente cubre todos los distritos de Madrid?", "Sí, cubrimos <strong>todos los distritos</strong>: Centro, Salamanca, Chamberí, Chamartín, Retiro, Tetuán, y municipios del sur como Móstoles, Getafe, Leganés y Fuenlabrada."),
         ("¿Cuánto cuesta el servicio urgente?", "Desde <strong>60€ + recargo de urgencia</strong>. Te damos el precio exacto en el presupuesto instantáneo."),
         ("¿Qué documentos necesito?", "DNI/NIE del propietario y escritura o nota simple del inmueble."),
     ]},
    {"slug": "precio-certificado-energetico-madrid", "title": "Precio del Certificado Energético en Madrid — Desde 60€ | Guía 2026",
     "desc": "Precio real del certificado energético en Madrid en 2026. Compara por distritos (Centro, Chamberí, Salamanca…). Desde 60€. Presupuesto gratuito sin compromiso.",
     "h1": "Precio del certificado energético <span>en Madrid</span>",
     "lead": "Compara precios reales del certificado de eficiencia energética (CEE) en Madrid capital y comunidad. Desde <strong>60€</strong> en distritos periféricos, desde <strong>69€</strong> en el centro. Todo incluido, sin sorpresas.",
     "city": "Madrid", "cp": "28001", "price": 60, "zone": "Madrid",
     "provincia": "Madrid", "keyword": "precio certificado energético Madrid",
     "tasa_org": "Dirección General de Industria, Energía y Minas",
     "tasa_url": "https://www.comunidad.madrid/servicios/energia/",
     "faq": [
         ("¿Cuánto cuesta un certificado energético en Madrid?", "El precio oscila entre <strong>60-96€</strong> para un piso estándar según el distrito. En el centro (Salamanca, Retiro) desde 75€, en la periferia (Fuenlabrada) desde 50€."),
         ("¿Por qué varía el precio según el distrito?", "La demanda de técnicos y los desplazamientos influyen. Los distritos céntricos tienen precios ligeramente más altos."),
         ("¿Qué incluye el precio?", "Visita técnica, cálculo con software oficial (CE3X/HULC), emisión del certificado con etiqueta energética, y registro telemático en la Comunidad de Madrid."),
         ("¿Cómo se compara con la competencia?", "CertiMadrid desde 69€, EcoCertifica desde 79€, CertiGreen desde 65€. En CertificadoYa desde 60€."),
     ]},
    {"slug": "certificado-energetico-barato-madrid", "title": "Certificado Energético Barato en Madrid — Desde 50€ | El Mejor Precio",
     "desc": "Certificado energético más barato de Madrid. Desde 50€ en distritos sur (Fuenlabrada, Leganés, Getafe). Presupuesto instantáneo. Técnicos verificados.",
     "h1": "Certificado energético barato <span>en Madrid</span>",
     "lead": "El <strong>certificado energético más barato de Madrid</strong> sin perder calidad. Desde <strong>50€</strong> en la zona sur (Fuenlabrada, Leganés, Getafe, Móstoles). Técnicos colegiados verificados.",
     "city": "Madrid", "cp": "28001", "price": 50, "zone": "Madrid",
     "provincia": "Madrid", "keyword": "certificado energético barato Madrid",
     "tasa_org": "Dirección General de Industria, Energía y Minas",
     "tasa_url": "https://www.comunidad.madrid/servicios/energia/",
     "faq": [
         ("¿Dónde es más barato el certificado energético en Madrid?", "En la zona sur: <strong>Fuenlabrada (50€), Leganés (55€), Getafe (55€), Móstoles (55€), Alcorcón (55€)</strong>. En el centro desde 69€."),
         ("¿Por qué es más barato en la zona sur?", "Mayor densidad de viviendas de tipología similar y más disponibilidad de técnicos en la zona."),
         ("¿El precio barato afecta a la calidad?", "No. Todos nuestros técnicos están colegiados y usan software oficial. El precio más bajo refleja eficiencia operativa, no menor calidad."),
         ("¿Puedo conseguir el certificado por 50€ en el centro?", "El precio mínimo en el centro es de 69€ por el mayor coste de desplazamiento de los técnicos."),
     ]},
    {"slug": "certificado-energetico-alquiler-madrid", "title": "Certificado Energético para Alquilar en Madrid — Obligatorio | Desde 50€",
     "desc": "Certificado energético obligatorio para alquilar vivienda en Madrid. Desde 50€ en zona sur, desde 69€ en centro. Evita multas de hasta 6.000€.",
     "h1": "Certificado energético para alquilar <span>en Madrid</span>",
     "lead": "Si vas a <strong>alquilar tu vivienda en Madrid</strong>, necesitas el certificado de eficiencia energética por ley. Te lo gestionamos desde <strong>50€</strong> en la zona sur.",
     "city": "Madrid", "cp": "28001", "price": 50, "zone": "Madrid",
     "provincia": "Madrid", "keyword": "certificado energético alquiler Madrid",
     "tasa_org": "Dirección General de Industria, Energía y Minas",
     "tasa_url": "https://www.comunidad.madrid/servicios/energia/",
     "faq": [
         ("¿Es obligatorio para alquilar en Madrid?", "Sí, desde 2013 es <strong>obligatorio</strong>. Multas de hasta 6.000€."),
         ("¿Cuánto cuesta para un piso de alquiler?", "Desde <strong>50€</strong> en Fuenlabrada, 55€ en Leganés/Getafe, y desde <strong>69€</strong> en el centro."),
         ("¿Quién lo paga?", "El <strong>propietario/casero</strong> es el responsable legal."),
         ("¿Es válido para una habitación?", "Si alquilas la vivienda completa, sí necesitas el CEE. Para alquiler por habitaciones, la normativa es menos clara, pero recomendamos tenerlo."),
     ]},
    {"slug": "certificado-energetico-venta-vivienda-madrid", "title": "Certificado Energético para Vender Piso en Madrid | Desde 50€",
     "desc": "Vende tu piso en Madrid con el certificado energético obligatorio. Desde 50€. Técnicos verificados. Presupuesto instantáneo. Todos los distritos.",
     "h1": "Certificado energético para vender tu piso <span>en Madrid</span>",
     "lead": "Si estás vendiendo tu vivienda en Madrid, necesitas el certificado de eficiencia energética. Te lo gestionamos desde <strong>50€</strong>, con técnicos verificados en todos los distritos.",
     "city": "Madrid", "cp": "28001", "price": 50, "zone": "Madrid",
     "provincia": "Madrid", "keyword": "certificado energético venta vivienda Madrid",
     "tasa_org": "Dirección General de Industria, Energía y Minas",
     "tasa_url": "https://www.comunidad.madrid/servicios/energia/",
     "faq": [
         ("¿Necesito el certificado para vender en Madrid?", "Sí, <strong>obligatorio</strong>. El notario te lo exigirá en la firma."),
         ("¿Cuánto cuesta?", "Desde <strong>50€</strong> en zona sur, desde <strong>69€</strong> en el centro."),
         ("¿Afecta la letra al precio de venta?", "Sí. Una buena calificación puede revalorizar tu piso entre un 5% y un 20%."),
         ("¿Cuánto tarda?", "48-72h estándar, <strong>24h en servicio urgente</strong>."),
     ]},
    {"slug": "certificado-energetico-mismo-dia-madrid", "title": "Certificado Energético en el Mismo Día — Madrid | Servicio Exprés",
     "desc": "Certificado energético en el mismo día en Madrid. Servicio exprés: visita y emisión en 24h. Técnicos verificados. Presupuesto instantáneo.",
     "h1": "Certificado energético <span>en el mismo día</span> en Madrid",
     "lead": "¿Necesitas el certificado de eficiencia energética <strong>hoy mismo</strong> en Madrid? Servicio exprés: el técnico visita tu inmueble en horas y el certificado está listo en el día. Presupuesto al instante.",
     "city": "Madrid", "cp": "28001", "price": 80, "zone": "Madrid",
     "provincia": "Madrid", "keyword": "certificado energético mismo día Madrid",
     "tasa_org": "Dirección General de Industria, Energía y Minas",
     "tasa_url": "https://www.comunidad.madrid/servicios/energia/",
     "faq": [
         ("¿Es posible tener el certificado en el mismo día?", "Sí, con nuestro <strong>servicio exprés</strong>. Un técnico acude en horas y el certificado se emite y registra en el mismo día."),
         ("¿Cuánto cuesta el servicio mismo día?", "Desde <strong>80€</strong> para un piso estándar, con recargo de urgencia incluido."),
         ("¿En qué zonas de Madrid está disponible?", "En <strong>toda la Comunidad de Madrid</strong>: capital, zona sur, norte y corredor del Henares."),
         ("¿Qué necesito para el servicio mismo día?", "DNI/NIE y la referencia catastral o dirección. Con eso podemos empezar el trámite de inmediato."),
     ]},
]


def make_city_page(data):
    """Generate a city landing page from Madrid template."""
    c = data["city"]
    slug = data["slug"]
    cp = data["cp"]
    price = data["price"]
    lead = data["lead_text"]
    market_low = data.get("market_low", price)
    market_high = data.get("market_high", price * 2)

    page = template

    # ── Head replacements ──
    page = page.replace(
        "<title>Certificado Energético en Madrid — Presupuesto en 24h | Desde 60€</title>",
        f"<title>Certificado Energético en {c} — Presupuesto en 24h | Desde {price}€</title>"
    )
    page = page.replace(
        '<meta name="description" content="Certificado de eficiencia energética (CEE) en Madrid. Presupuesto instantáneo por m². Técnicos verificados en Madrid capital y comunidad. Desde 60€. Entrega en 24-48h.">',
        f'<meta name="description" content="Certificado de eficiencia energética (CEE) en {c}. Presupuesto instantáneo por m². Técnicos verificados en {c}. Desde {price}€. Entrega en 24-48h.">'
    )
    page = page.replace(
        '<meta name="keywords" content="certificado energético Madrid, CEE Madrid, precio certificado energético Madrid, técnico certificador Madrid">',
        f'<meta name="keywords" content="certificado energético {c}, CEE {c}, precio certificado energético {c}, técnico certificador {c}">'
    )
    page = page.replace(
        '<link rel="canonical" href="https://www.certificadoya.es/certificado-energetico-madrid">',
        f'<link rel="canonical" href="https://www.certificadoya.es/{slug}">'
    )

    # ── OG tags ──
    page = page.replace(
        '<meta property="og:title" content="Certificado Energético en Madrid — Presupuesto en 24h | Desde 60€">',
        f'<meta property="og:title" content="Certificado Energético en {c} — Presupuesto en 24h | Desde {price}€">'
    )
    page = page.replace(
        '<meta property="og:description" content="Presupuesto instantáneo para tu certificado energético en Madrid. Técnicos verificados en Madrid capital y comunidad. Desde 60-96€ para un piso estándar.">',
        f'<meta property="og:description" content="Presupuesto instantáneo para tu certificado energético en {c}. Técnicos verificados. Desde {market_low}-{market_high}€ para un piso estándar.">'
    )
    page = page.replace(
        '<meta property="og:url" content="https://www.certificadoya.es/certificado-energetico-madrid">',
        f'<meta property="og:url" content="https://www.certificadoya.es/{slug}">'
    )

    # ── Twitter cards ──
    page = page.replace(
        '<meta name="twitter:title" content="Certificado Energético en Madrid — Desde 60€">',
        f'<meta name="twitter:title" content="Certificado Energético en {c} — Desde {price}€">'
    )
    page = page.replace(
        '<meta name="twitter:description" content="Técnicos verificados en Madrid capital y comunidad. Presupuesto al instante.">',
        f'<meta name="twitter:description" content="Técnicos verificados en {c}. Presupuesto al instante.">'
    )

    # ── Schema: LocalBusiness and BreadcrumbList ──
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
    page = page.replace(
        '"name": "Certificado energético en Madrid"',
        f'"name": "Certificado energético en {c}"'
    )

    # ── Body: Breadcrumb ──
    page = page.replace(
        '› Certificado energético en Madrid',
        f'› Certificado energético en {c}'
    )

    # ── Hero H1 ──
    page = page.replace(
        '<h1>Certificado energético <span>en Madrid</span></h1>',
        f'<h1>Certificado energético <span>en {c}</span></h1>'
    )
    page = page.replace(
        '<p class="lead">Presupuesto al instante para tu certificado de eficiencia energética (CEE) en Madrid capital y comunidad. Técnicos colegiados verificados. Resultado en 24-48 horas.</p>',
        f'<p class="lead">Presupuesto al instante para tu certificado de eficiencia energética (CEE) en {c}. Técnicos colegiados verificados. Resultado en 24-48 horas.</p>'
    )

    # ── Calculator card ──
    page = page.replace('en Madrid</h3>', f'en {c}</h3>')
    page = page.replace('placeholder="Ej: 28001"', f'placeholder="Ej: {cp}"')

    # ── Content section: title ──
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

    # ── Pricing grid ──
    p1 = price
    p2 = max(price, int(price * 1.3))
    p3 = int(price * 1.5)
    p4 = max(price, 75)
    page = page.replace('60-96€', f'{p1}-{p2}€')
    # Second occurrence
    page = page.replace(f'<span>{p1}-{p2}€</span>', f'<span>{p1}-{p2}€</span>', 1)  # no-op, already done
    # Fix the remaining Madrid price references
    page = page.replace('<span>Desde 96€</span>', f'<span>Desde {p2}€</span>')
    page = page.replace('<span>121-156€</span>', f'<span>{p3}-{int(p3 * 1.3)}€</span>')
    page = page.replace('<span>Desde 75€</span>', f'<span>Desde {p4}€</span>')

    # ── Why choose us ──
    page = page.replace('en Madrid?</h3>', f'en {c}?</h3>')
    page = page.replace(
        '<li><strong>Técnicos colegiados en Madrid</strong>: arquitectos, aparejadores e ingenieros verificados</li>',
        f'<li><strong>Técnicos colegiados en {c}</strong>: arquitectos, aparejadores e ingenieros verificados</li>'
    )

    # ── FAQ ──
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

    # ── Tasa aviso ──
    page = page.replace(
        'Dirección General de Industria',
        'Dirección General de Energía, Minería y Reactivación'
    )
    page = page.replace(
        'https://www.comunidad.madrid/servicios/energia/',
        'https://sede.asturias.es/'
    )

    # ── CTA band ──
    page = page.replace(
        '¿Necesitas tu certificado energético en Madrid?</p>',
        f'¿Necesitas tu certificado energético en {c}?</p>'
    )

    # ── CTA técnicos ──
    page = page.replace(
        'en Madrid te contactará',
        f'en {c} te contactará'
    )
    page = page.replace(
        "localidad: 'Madrid',",
        f"localidad: '{c}',"
    )
    page = page.replace(
        "'provincia': 'Madrid'",
        f"'provincia': 'Asturias'"
    )
    page = page.replace(
        "cp.value || '28001'",
        f"cp.value || '{cp}'"
    )
    page = page.replace(
        "params.get('cp') || '28001'",
        f"params.get('cp') || '{cp}'"
    )

    # ── "en tu zona" fix ──
    page = page.replace(
        'Recibe clientes en tu zona',
        f'Recibe clientes en {c}'
    )
    page = page.replace(
        "'+ nombre + '! Un técnico en Madrid te contactará",
        f"'+ nombre + '! Un técnico en {c} te contactará"
    )

    os.makedirs(f'{BASE}/{slug}', exist_ok=True)
    with open(f'{BASE}/{slug}/index.html', 'w') as f:
        f.write(page)
    return slug


def make_trans_page(data):
    """Generate a transaccional landing page."""
    slug = data["slug"]
    title = data["title"]
    desc = data["desc"]
    h1 = data["h1"]
    lead = data["lead"]
    city = data["city"]
    cp = data["cp"]
    price = data["price"]
    zone = data["zone"]
    provincia = data["provincia"]
    tasa_org = data["tasa_org"]
    tasa_url = data["tasa_url"]
    faqs = data.get("faq", [])

    page = template

    # ── Head ──
    page = page.replace(
        "<title>Certificado Energético en Madrid — Presupuesto en 24h | Desde 60€</title>",
        f"<title>{title}</title>"
    )
    page = page.replace(
        '<meta name="description" content="Certificado de eficiencia energética (CEE) en Madrid. Presupuesto instantáneo por m². Técnicos verificados en Madrid capital y comunidad. Desde 60€. Entrega en 24-48h.">',
        f'<meta name="description" content="{desc}">'
    )
    page = page.replace(
        '<meta name="keywords" content="certificado energético Madrid, CEE Madrid, precio certificado energético Madrid, técnico certificador Madrid">',
        f'<meta name="keywords" content="certificado energético {city}, CEE {city}, {data.get("keyword", "")}">'
    )
    page = page.replace(
        '<link rel="canonical" href="https://www.certificadoya.es/certificado-energetico-madrid">',
        f'<link rel="canonical" href="https://www.certificadoya.es/{slug}">'
    )

    # ── OG ──
    page = page.replace(
        '<meta property="og:title" content="Certificado Energético en Madrid — Presupuesto en 24h | Desde 60€">',
        f'<meta property="og:title" content="{title}">'
    )
    page = page.replace(
        '<meta property="og:description" content="Presupuesto instantáneo para tu certificado energético en Madrid. Técnicos verificados en Madrid capital y comunidad. Desde 60-96€ para un piso estándar.">',
        f'<meta property="og:description" content="{desc[:200]}">'
    )
    page = page.replace(
        '<meta property="og:url" content="https://www.certificadoya.es/certificado-energetico-madrid">',
        f'<meta property="og:url" content="https://www.certificadoya.es/{slug}">'
    )

    # ── Twitter ──
    page = page.replace(
        '<meta name="twitter:title" content="Certificado Energético en Madrid — Desde 60€">',
        f'<meta name="twitter:title" content="{title[:70]}">'
    )
    page = page.replace(
        '<meta name="twitter:description" content="Técnicos verificados en Madrid capital y comunidad. Presupuesto al instante.">',
        f'<meta name="twitter:description" content="{desc[:150]}">'
    )

    # ── Schema LocalBusiness ──
    page = page.replace(
        '"name": "CertificadoYa — Certificado Energético en Madrid"',
        f'"name": "CertificadoYa — {title[:60]}"'
    )
    page = page.replace(
        '"description": "Certificados de eficiencia energética (CEE) en Madrid. Técnicos verificados. Presupuesto instantáneo."',
        f'"description": "{desc[:120]}"'
    )
    page = page.replace(
        '"url": "https://www.certificadoya.es/certificado-energetico-madrid"',
        f'"url": "https://www.certificadoya.es/{slug}"'
    )
    page = page.replace(
        '"name": "Madrid"',
        f'"name": "{city}"'
    )
    page = page.replace(
        '"addressLocality": "Madrid"',
        f'"addressLocality": "{city}"'
    )
    page = page.replace(
        '"name": "Certificado Energético (CEE) en Madrid"',
        f'"name": "Certificado Energético (CEE) en {city}"'
    )
    page = page.replace(
        '"description": "Emisión y registro del CEE por técnico colegiado en Madrid capital y comunidad"',
        f'"description": "Emisión y registro del CEE por técnico colegiado en {city}"'
    )
    page = page.replace(
        '"price": 60,',
        f'"price": {price},'
    )
    page = page.replace(
        '"minPrice": 60',
        f'"minPrice": {price}'
    )
    page = page.replace(
        '"name": "Certificado energético en Madrid"',
        f'"name": "Certificado energético en {city}"'
    )

    # ── Breadcrumb ──
    page = page.replace(
        '› Certificado energético en Madrid',
        f'› {title[:60]}'
    )

    # ── H1 and lead ──
    page = page.replace(
        '<h1>Certificado energético <span>en Madrid</span></h1>',
        f'<h1>{h1}</h1>'
    )
    page = page.replace(
        '<p class="lead">Presupuesto al instante para tu certificado de eficiencia energética (CEE) en Madrid capital y comunidad. Técnicos colegiados verificados. Resultado en 24-48 horas.</p>',
        f'<p class="lead">{lead}</p>'
    )

    # ── Calculator ──
    page = page.replace('en Madrid</h3>', f'en {city}</h3>')
    page = page.replace('placeholder="Ej: 28001"', f'placeholder="Ej: {cp}"')

    # ── Content title ──
    page = page.replace(
        '<h2>Certificado energético en Madrid: rápido, fácil y al mejor precio</h2>',
        f'<h2>{title}</h2>'
    )

    # ── Pricing grid ──
    p1 = price
    p2 = max(price, int(price * 1.3))
    p3 = int(price * 1.5)
    p4 = max(price, 75)
    page = page.replace('60-96€', f'{p1}-{p2}€')
    page = page.replace(f'<span>{p1}-{p2}€</span>', f'<span>{p1}-{p2}€</span>', 1)  # no-op
    page = page.replace('<span>Desde 96€</span>', f'<span>Desde {p2}€</span>')
    page = page.replace('<span>121-156€</span>', f'<span>{p3}-{int(p3 * 1.3)}€</span>')
    page = page.replace('<span>Desde 75€</span>', f'<span>Desde {p4}€</span>')

    # ── Why choose us ──
    page = page.replace('en Madrid?</h3>', f'en {city}?</h3>')
    page = page.replace(
        '<li><strong>Técnicos colegiados en Madrid</strong>: arquitectos, aparejadores e ingenieros verificados</li>',
        f'<li><strong>Técnicos colegiados en {city}</strong>: arquitectos, aparejadores e ingenieros verificados</li>'
    )

    # ── FAQ: replace the FAQ section ──
    if faqs:
        # Remove existing FAQ block and replace
        faq_start = page.find('Preguntas frecuentes sobre el CEE en Madrid</h3>')
        if faq_start > 0:
            # Find the closing of the faq section (next </section> or tasa-aviso)
            faq_header = 'Preguntas frecuentes sobre el CEE en Madrid</h3>'
            page = page.replace(faq_header, f'Preguntas frecuentes sobre el CEE en {city}</h3>')
            # Replace the two FAQ items with our new ones
            # Find first FAQ item
            first_faq = page.find('<details class="faq-item">')
            # Find start of tasa-aviso
            tasa_start = page.find('<div class="tasa-aviso">')
            if first_faq > 0 and tasa_start > first_faq:
                # Build new FAQ HTML
                faq_html = '\n'
                for q, a in faqs:
                    faq_html += f'''    <details class="faq-item">
      <summary class="faq-question">{q}</summary>
      <div class="faq-answer"><p>{a}</p></div>
    </details>\n'''
                # Replace from first FAQ to before tasa-aviso
                before = page[:first_faq]
                after_tasa = page[tasa_start:]
                page = before + faq_html + '\n  </section>\n\n  ' + after_tasa

    # ── Tasa aviso ──
    page = page.replace(
        'Dirección General de Industria',
        tasa_org
    )
    page = page.replace(
        'https://www.comunidad.madrid/servicios/energia/',
        tasa_url
    )

    # ── CTA band ──
    page = page.replace(
        '¿Necesitas tu certificado energético en Madrid?</p>',
        f'¿Necesitas tu certificado energético en {city}?</p>'
    )

    # ── CTA técnicos + JS ──
    page = page.replace(
        'en Madrid te contactará',
        f'en {city} te contactará'
    )
    page = page.replace(
        "localidad: 'Madrid',",
        f"localidad: '{city}',"
    )
    page = page.replace(
        "'provincia': 'Madrid'",
        f"'provincia': '{provincia}'"
    )
    page = page.replace(
        "cp.value || '28001'",
        f"cp.value || '{cp}'"
    )
    page = page.replace(
        "params.get('cp') || '28001'",
        f"params.get('cp') || '{cp}'"
    )
    page = page.replace(
        'Recibe clientes en tu zona',
        f'Recibe clientes en {city}'
    )
    page = page.replace(
        "'+ nombre + '! Un técnico en Madrid te contactará",
        f"'+ nombre + '! Un técnico en {city} te contactará"
    )

    os.makedirs(f'{BASE}/{slug}', exist_ok=True)
    with open(f'{BASE}/{slug}/index.html', 'w') as f:
        f.write(page)
    return slug


# ── Run ──
print("🏗️  Generando landings de ciudades Asturias...")
for city_data in ASTURIAS_CITIES:
    slug = make_city_page(city_data)
    print(f"  ✅ {slug}")

print("\n🏗️  Generando landings transaccionales Asturias...")
for trans in AST_TRANS:
    slug = make_trans_page(trans)
    print(f"  ✅ {slug}")

print("\n🏗️  Generando landings transaccionales Madrid...")
for trans in MAD_TRANS:
    slug = make_trans_page(trans)
    print(f"  ✅ {slug}")

print(f"\n🎉 ¡{len(ASTURIAS_CITIES) + len(AST_TRANS) + len(MAD_TRANS)} páginas generadas!")
