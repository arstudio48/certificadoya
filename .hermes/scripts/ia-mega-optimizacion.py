#!/usr/bin/env python3
"""
MEGA-Optimización IA + SEO para CertificadoYa.
Ejecuta en paralelo: FAQPage + Referencias BOE.
"""
import re, os, json, glob

BLOG_DIR = 'C:/Users/artur/certificadoya/blog'
# Artículos que NO son contenido real (redirecciones, plantillas, tests)
SKIP = {'test-write2.html', 'certificado-energetico-obligatorio-2026-v2.html', 'plantilla-informe-energetico.html'}

def get_topic_tags(html, filename):
    """Detectar categoría del artículo por su contenido."""
    text = html.lower()
    if 'subvencion' in text or 'ayuda' in text or 'rehabilitacion' in text:
        return 'subvenciones'
    if 'precio' in text or 'coste' in text or 'tarifa' in text or '45€' in text or 'presupuesto' in text:
        return 'precios'
    if 'normativa' in text or 'rd ' in text or 'real decreto' in text or 'obligatorio' in text or 'ley' in text:
        return 'normativa'
    if 'tecnico' in text or 'certificador' in text or 'ce3x' in text or 'hulc' in text or 'registro' in text:
        return 'tecnicos'
    if 'caducidad' in text or 'cedula' in text or 'hipoteca' in text or 'banco' in text:
        return 'basico'
    if 'online' in text or 'internet' in text or 'digital' in text:
        return 'tecnologia'
    return 'basico'

# Bancos de FAQ por categoría
FAQ_TEMPLATES = {
    'normativa': [
        {"q": "¿Cuál es la normativa vigente del certificado energético?", "a": "La normativa principal es el Real Decreto 235/2013, modificado por el RD 659/2025, que transpone la Directiva Europea 2010/31/UE. Esta normativa establece la obligatoriedad del CEE para venta y alquiler, así como los requisitos técnicos mínimos."},
        {"q": "¿Qué sanciones hay por no tener el certificado energético?", "a": "Las sanciones varían por comunidad autónoma pero pueden oscilar entre 300€ y 6.000€ para infracciones leves, y hasta 100.000€ en casos graves de reiteración o fraude."},
        {"q": "¿El certificado energético caduca aunque la normativa cambie?", "a": "Sí, el certificado tiene una validez máxima de 10 años. Sin embargo, si cambia la normativa aplicable (como con el RD 659/2025), es recomendable actualizarlo para reflejar los nuevos criterios."},
        {"q": "¿Es obligatorio el certificado energético para alquileres turísticos?", "a": "Sí, desde la entrada en vigor del RD 659/2025, los alquileres de corta duración y vacacionales también están obligados a disponer de certificado energético y mostrar la etiqueta en los anuncios."}
    ],
    'subvenciones': [
        {"q": "¿Qué ayudas existen para rehabilitación energética en 2026?", "a": "El Plan de Rehabilitación de Viviendas 2026 incluye ayudas de hasta 21.400€ por vivienda para mejoras de eficiencia energética, financiadas con fondos Next Generation EU. Cada comunidad autónoma gestiona su convocatoria."},
        {"q": "¿Cuánto se puede ahorrar con subvenciones para mejorar la eficiencia?", "a": "Dependiendo de la mejora, las ayudas cubren entre el 40% y el 80% del coste. Por ejemplo, cambiar ventanas puede tener ayudas del 40%, mientras que una rehabilitación integral puede llegar al 80%."},
        {"q": "¿Se puede solicitar una ayuda sin tener el certificado energético?", "a": "La mayoría de las ayudas exigen tener el CEE en vigor como requisito previo, ya que necesitan la calificación actual para justificar la mejora. Es recomendable obtenerlo antes de solicitar la ayuda."},
        {"q": "¿Qué plazo hay para solicitar las ayudas Next Generation?", "a": "Los plazos varían por comunidad autónoma. La mayoría de convocatorias están abiertas hasta finales de 2026 o hasta agotar presupuesto. Se recomienda solicitarlas cuanto antes por la alta demanda."}
    ],
    'precios': [
        {"q": "¿Cuánto cuesta un certificado energético en 2026?", "a": "El precio del certificado energético varía según la provincia, el tipo de inmueble y la superficie. En CertificadoYa ofrecemos precios desde 45€ (IVA no incluido), con presupuesto instantáneo sin compromiso."},
        {"q": "¿Qué incluye el precio del certificado energético?", "a": "El precio incluye la visita del técnico, la recogida de datos del inmueble, el cálculo mediante software homologado (CE3X), la emisión del certificado y su registro en la comunidad autónoma correspondiente."},
        {"q": "¿El precio del certificado es el mismo para una casa que para un piso?", "a": "Generalmente no. El precio depende de la superficie, la complejidad del inmueble y la provincia. Las viviendas unifamiliares suelen tener un coste mayor que los pisos por su mayor superficie y complejidad."},
        {"q": "¿Puedo pagar el certificado energético a plazos?", "a": "En CertificadoYa pagas solo cuando el técnico acepta tu encargo. No hay pagos por adelantado ni cuotas fijas. El pago se realiza contra la entrega del certificado registrado."}
    ],
    'tecnicos': [
        {"q": "¿Qué requisitos necesita un técnico para ser certificador?", "a": "Para ser técnico certificador necesitas titulación habilitante (arquitecto, ingeniero, arquitecto técnico o ingeniero técnico) y darte de alta en el registro de la comunidad autónoma correspondiente."},
        {"q": "¿Cuánto cobra un técnico por un certificado energético?", "a": "Los honorarios de los técnicos certificadores varían entre 30€ y 120€ por certificado, dependiendo de la complejidad del inmueble, la provincia y la competencia en la zona."},
        {"q": "¿Qué software necesito para hacer certificados energéticos?", "a": "Los programas más utilizados son CE3X (el más extendido), HULC (Herramienta Unificada LIDER-CALENER) y CYPETHERM. CE3X es el más recomendado por su facilidad de uso y aceptación en todas las CCAA."},
        {"q": "¿Es obligatorio estar registrado en la comunidad autónoma?", "a": "Sí, es obligatorio estar inscrito en el registro de certificadores de la comunidad autónoma donde se emita el certificado. Cada CCAA tiene su propio registro y procedimiento."}
    ],
    'basico': [
        {"q": "¿Qué es el certificado de eficiencia energética?", "a": "El certificado de eficiencia energética (CEE) es un documento oficial que califica el consumo energético de un inmueble mediante una escala de letras de la A (más eficiente) a la G (menos eficiente). Es obligatorio para vender o alquilar."},
        {"q": "¿Cuánto dura el certificado energético?", "a": "El certificado energético tiene una validez máxima de 10 años. Los certificados con calificación A o B caducan a los 10 años, mientras que el resto caducan a los 5 años desde su emisión."},
        {"q": "¿Dónde se registra el certificado energético?", "a": "El certificado debe registrarse en el órgano competente de la comunidad autónoma donde se ubique el inmueble. Cada CCAA tiene su propio registro (ej: ICAEN en Cataluña, AVEN en Comunidad Valenciana)."},
        {"q": "¿Qué diferencia hay entre certificado y etiqueta energética?", "a": "El certificado es el documento completo con todos los datos técnicos y cálculos. La etiqueta es un resumen visual con la calificación en letras que debe aparecer en los anuncios de venta o alquiler."}
    ],
    'tecnologia': [
        {"q": "¿Se puede hacer el certificado energético online?", "a": "Sí, puedes solicitar el certificado energético online a través de plataformas como CertificadoYa. Un técnico certificador se pondrá en contacto contigo para concertar la visita al inmueble."},
        {"q": "¿Cómo funciona la firma digital del certificado?", "a": "El certificado energético debe estar firmado digitalmente por el técnico certificador mediante un certificado electrónico reconocido. La firma digital garantiza su validez legal."},
        {"q": "¿Qué programas informáticos están homologados?", "a": "Los programas homologados para el cálculo de la calificación energética son CE3X, HULC, CYPETHERM, SG SAVE y otros. Todos deben estar aprobados por el Ministerio de Vivienda."},
        {"q": "¿Cuánto tarda en emitirse un certificado telemático?", "a": "Una vez realizada la visita al inmueble, el técnico suele emitir el certificado en un plazo de 24 a 48 horas hábiles. El registro en la CCAA puede tardar unos días adicionales."}
    ]
}

REF_BOE_BLOCK = """<div class="referencias-oficiales" style="margin-top:2.5rem;padding:1.2rem;background:#f9fbfc;border:1px solid #e2e8f0;border-radius:12px">
  <h3 style="font-size:1rem;margin:0 0 .8rem">📜 Referencias oficiales</h3>
  <ul style="margin:0;padding:0 0 0 1.2rem;font-size:.85rem;color:#4a5a6e">
    <li><a href="https://www.boe.es/buscar/doc.php?id=BOE-A-2013-8353" target="_blank" rel="nofollow">Real Decreto 235/2013, de 5 de abril</a> — Procedimiento básico para la certificación energética de edificios</li>
    <li><a href="https://www.boe.es/buscar/act.php?id=BOE-A-2025-12186" target="_blank" rel="nofollow">Real Decreto 659/2025, de 15 de julio</a> — Modificación del procedimiento de certificación energética</li>
    <li><a href="https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32010L0031" target="_blank" rel="nofollow">Directiva 2010/31/UE</a> — Eficiencia energética de los edificios (EPBD)</li>
    <li><a href="https://www.codigotecnico.org/" target="_blank" rel="nofollow">Código Técnico de la Edificación (CTE)</a> — Documento Básico de Ahorro de Energía (DB-HE)</li>
  </ul>
</div>
"""

def add_faq_schema(html):
    """Añade FAQPage schema si no existe."""
    if 'FAQPage' in html:
        return html, False
    
    # Detectar categoría
    cat = get_topic_tags(html, '')
    faqs = FAQ_TEMPLATES.get(cat, FAQ_TEMPLATES['basico'])
    
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }
    for faq in faqs:
        schema["mainEntity"].append({
            "@type": "Question",
            "name": faq["q"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq["a"]
            }
        })
    
    schema_html = '<script type="application/ld+json">\n' + json.dumps(schema, ensure_ascii=False, indent=2) + '\n</script>'
    
    # Insertar antes de </head>
    idx = html.find('</head>')
    if idx == -1:
        return html, False
    html = html[:idx] + schema_html + '\n' + html[idx:]
    return html, True

def add_boe_refs(html, filename):
    """Añade bloque de referencias oficiales si no existe."""
    if 'Real Decreto' in html or 'referencias-oficiales' in html:
        return html, False
    if filename in SKIP:
        return html, False
    
    # Insertar antes de <footer> o antes de </body>
    for marker in ['<footer', '</body>']:
        idx = html.find(marker)
        if idx != -1:
            html = html[:idx] + '\n' + REF_BOE_BLOCK + '\n' + html[idx:]
            return html, True
    return html, False

# Procesar todos los artículos
results = {'faq_added': [], 'boe_added': [], 'errors': []}
files = sorted(glob.glob(os.path.join(BLOG_DIR, '*.html')))

for fpath in files:
    fname = os.path.basename(fpath)
    if fname in SKIP:
        continue
    
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            html = f.read()
        
        changed = False
        
        # 1. FAQPage schema
        html2, faq_done = add_faq_schema(html)
        if faq_done:
            results['faq_added'].append(fname)
            changed = True
        
        # 2. Referencias BOE
        html3, boe_done = add_boe_refs(html2, fname)
        if boe_done:
            results['boe_added'].append(fname)
            changed = True
        
        if changed:
            # Backup
            # with open(fpath + '.bak', 'w', encoding='utf-8') as f:
            #     f.write(html)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(html3 if boe_done else html2)
            print(f'✅ {fname}')
        else:
            print(f'⏭️  {fname} (sin cambios)')
    
    except Exception as e:
        print(f'❌ {fname}: {e}')
        results['errors'].append(f'{fname}: {e}')

print(f'\n{"="*50}')
print(f'FAQPage añadido: {len(results["faq_added"])} artículos')
print(f'Referencias BOE añadidas: {len(results["boe_added"])} artículos')
print(f'Errores: {len(results["errors"])}')
print(f'{"="*50}')
