#!/usr/bin/env python3
"""
x2_inyectar_registro_ccaa.py — Inyecta bloque de registro autonómico CEE
en cada landing page provincial.

Los datos se extraen DIRECTAMENTE de organismos-contacto.html.
Prohibido inventar datos. Dato ausente = [[PENDIENTE]].
"""

import json
import os
import sys

BASE_DIR = "/home/arturo/certificadoya"
EXCLUIDAS = {"coruna"}  # stub redirect

# Datos extraídos de organismos-contacto.html
# Formato: CCAA_slug → {nombre, organismo, web, telefono, email}
ORGANISMOS_CCAA = {
    "andalucia": {
        "nombre_ccaa": "Andalucía",
        "organismo": "Agencia Andaluza de la Energía",
        "web": "https://www.agenciaandaluzadelaenergia.es/",
        "telefono": "954 78 63 35",
        "email": "informacion.aae@juntadeandalucia.es",
    },
    "aragon": {
        "nombre_ccaa": "Aragón",
        "organismo": "Dirección General de Energía y Minas — Gobierno de Aragón",
        "web": "https://www.aragon.es/-/certificacion-eficiencia-energetica-edificios",
        "telefono": "976 71 41 22",
        "email": "certificacionenergetica@aragon.es",
    },
    "asturias": {
        "nombre_ccaa": "Principado de Asturias",
        "organismo": "Dirección General de Energía, Minería y Reactivación",
        "web": "https://www.asturias.es/web/asturias/certificacion-energetica",
        "telefono": "985 10 57 00",
        "email": "eficienciaenergetica@asturias.org",
    },
    "baleares": {
        "nombre_ccaa": "Islas Baleares",
        "organismo": "Direcció General d'Energia i Canvi Climàtic",
        "web": "https://www.caib.es/govern/organigrama/area.do?coduo=4135",
        "telefono": "971 17 70 00",
        "email": "energia@caib.es",
    },
    "canarias": {
        "nombre_ccaa": "Canarias",
        "organismo": "Consejería de Transición Ecológica, Lucha contra el Cambio Climático y Planificación Territorial",
        "web": "https://www.gobiernodecanarias.org/energia/",
        "telefono": "922 47 33 00 / 928 11 70 00",
        "email": "dgenergia.ccpt@gobiernodecanarias.org",
    },
    "cantabria": {
        "nombre_ccaa": "Cantabria",
        "organismo": "Dirección General de Industria, Energía y Minas — Gobierno de Cantabria",
        "web": "https://www.cantabria.es/web/direccion-general-industria-energia-minas",
        "telefono": "942 20 84 00",
        "email": "industria@cantabria.es",
    },
    "castilla-leon": {
        "nombre_ccaa": "Castilla y León",
        "organismo": "Ente Regional de la Energía de Castilla y León (EREN)",
        "web": "https://www.eren.jcyl.es/",
        "telefono": "983 41 26 56",
        "email": "eren@jcyl.es",
    },
    "castilla-mancha": {
        "nombre_ccaa": "Castilla-La Mancha",
        "organismo": "Dirección General de Transición Energética — JCCM",
        "web": "https://www.castillalamancha.es/gobierno/desarrollosostenible",
        "telefono": "925 24 88 00",
        "email": "energia@jccm.es",
    },
    "cataluna": {
        "nombre_ccaa": "Cataluña",
        "organismo": "Institut Català d'Energia (ICAEN)",
        "web": "https://icaen.gencat.cat/es/energia/edificis/certificacio-energetica/",
        "telefono": "93 622 05 00",
        "email": "icaen.energia@gencat.cat",
    },
    "ceuta": {
        "nombre_ccaa": "Ceuta",
        "organismo": "Consejería de Medio Ambiente y Sostenibilidad — Ciudad Autónoma de Ceuta",
        "web": "http://www.ceuta.es/ceuta/medio-ambiente",
        "telefono": "856 20 05 00",
        "email": "medioambiente@ceuta.es",
    },
    "com-valenciana": {
        "nombre_ccaa": "Comunidad Valenciana",
        "organismo": "Instituto Valenciano de Competitividad e Innovación (IVACE+i) — Área de Energía",
        "web": "https://www.ivace.es/energia",
        "telefono": "96 120 99 00",
        "email": "energia_ivace@gva.es",
    },
    "extremadura": {
        "nombre_ccaa": "Extremadura",
        "organismo": "Agencia Extremeña de la Energía (AGENEX)",
        "web": "https://www.agenex.net/",
        "telefono": "924 26 21 61",
        "email": "agenex@agenex.net",
    },
    "galicia": {
        "nombre_ccaa": "Galicia",
        "organismo": "Instituto Enerxético de Galicia (INEGA)",
        "web": "https://www.inega.gal/",
        "telefono": "981 54 15 00",
        "email": "inega.info@xunta.gal",
    },
    "la-rioja": {
        "nombre_ccaa": "La Rioja",
        "organismo": "Dirección General de Transición Energética y Cambio Climático",
        "web": "https://www.larioja.org/energia/es",
        "telefono": "941 29 11 00",
        "email": "dgenergia@larioja.org",
    },
    "madrid": {
        "nombre_ccaa": "Comunidad de Madrid",
        "organismo": "Fundación de la Energía de la Comunidad de Madrid (FENERCOM)",
        "web": "https://www.fenercom.com/",
        "telefono": "91 353 21 00",
        "email": "consultas@fenercom.com",
    },
    "murcia": {
        "nombre_ccaa": "Región de Murcia",
        "organismo": "Dirección General de Energía y Actividad Industrial y Minera — CARM",
        "web": "https://www.carm.es/web/pagina?IDCONTENIDO=3433",
        "telefono": "968 36 60 00",
        "email": "dgindustriaenergia@carm.es",
    },
    "navarra": {
        "nombre_ccaa": "Navarra",
        "organismo": "Departamento de Desarrollo Económico y Empresarial — Gobierno de Navarra",
        "web": "https://www.navarra.es/es/transicion-energetica",
        "telefono": "848 42 77 00",
        "email": "energia@navarra.es",
    },
    "pais-vasco": {
        "nombre_ccaa": "País Vasco",
        "organismo": "Ente Vasco de la Energía (EVE)",
        "web": "https://www.eve.eus/",
        "telefono": "944 03 56 00",
        "email": "eve@eve.eus",
    },
    "melilla": {
        "nombre_ccaa": "Melilla",
        "organismo": "Consejería de Medio Ambiente y Sostenibilidad — Ciudad Autónoma de Melilla",
        "web": "http://www.melilla.es/melillaportal/contenedor.jsp?seccion=s_floc_d4_v1.jsp",
        "telefono": "952 69 91 00",
        "email": "medioambiente@melilla.es",
    },
}

# Mapeo provincia → CCAA
PROVINCIA_A_CCAA = {
    "a-coruna": "galicia",
    "alava": "pais-vasco",
    "albacete": "castilla-mancha",
    "alcala-de-henares": "madrid",
    "alcobendas": "madrid",
    "alcorcon": "madrid",
    "alicante": "com-valenciana",
    "almeria": "andalucia",
    "alquiler-asturias": "asturias",
    "alquiler-madrid": "madrid",
    "asturias": "asturias",
    "avila": "castilla-leon",
    "aviles": "asturias",
    "badajoz": "extremadura",
    "baleares": "baleares",
    "barato-madrid": "madrid",
    "barcelona": "cataluna",
    "benidorm": "com-valenciana",
    "bilbao": "pais-vasco",
    "bizkaia": "pais-vasco",
    "burgos": "castilla-leon",
    "caceres": "extremadura",
    "cadiz": "andalucia",
    "cantabria": "cantabria",
    "castellon": "com-valenciana",
    "ceuta": "ceuta",
    "chamartin": "madrid",
    "chamberi": "madrid",
    "ciudad-real": "castilla-mancha",
    "cordoba": "andalucia",
    "cuenca": "castilla-mancha",
    "fuenlabrada": "madrid",
    "getafe": "madrid",
    "gijon": "asturias",
    "gipuzkoa": "pais-vasco",
    "girona": "cataluna",
    "granada": "andalucia",
    "guadalajara": "castilla-mancha",
    "huelva": "andalucia",
    "huesca": "aragon",
    "jaen": "andalucia",
    "la-rioja": "la-rioja",
    "langreo": "asturias",
    "las-palmas": "canarias",
    "leganes": "madrid",
    "leon": "castilla-leon",
    "lleida": "cataluna",
    "lugo": "galicia",
    "madrid": "madrid",
    "madrid-centro": "madrid",
    "malaga": "andalucia",
    "melilla": "melilla",
    "mieres": "asturias",
    "mismo-dia-madrid": "madrid",
    "mostoles": "madrid",
    "murcia": "murcia",
    "navarra": "navarra",
    "ourense": "galicia",
    "oviedo": "asturias",
    "palencia": "castilla-leon",
    "pontevedra": "galicia",
    "pozuelo": "madrid",
    "precio-asturias": "asturias",
    "retiro": "madrid",
    "salamanca": "castilla-leon",
    "salamanca-madrid": "madrid",
    "segovia": "castilla-leon",
    "sevilla": "andalucia",
    "siero": "asturias",
    "soria": "castilla-leon",
    "tarragona": "cataluna",
    "tenerife": "canarias",
    "teruel": "aragon",
    "tetuan": "madrid",
    "toledo": "castilla-mancha",
    "urgente-asturias": "asturias",
    "urgente-madrid": "madrid",
    "valencia": "com-valenciana",
    "valladolid": "castilla-leon",
    "venta-vivienda-asturias": "asturias",
    "venta-vivienda-madrid": "madrid",
    "villaviciosa": "asturias",
    "zamora": "castilla-leon",
    "zaragoza": "aragon",
}


def generar_bloque_registro(slug):
    """Genera el HTML del bloque de registro CCAA para una provincia."""
    ccaa_slug = PROVINCIA_A_CCAA.get(slug)
    if not ccaa_slug:
        return None

    org = ORGANISMOS_CCAA.get(ccaa_slug)
    if not org:
        print(f"⚠️  {slug}: no hay datos para CCAA '{ccaa_slug}' — usando [[PENDIENTE]]")
        return f"""        <section class="registro-ccaa">
            <h2>Registro autonómico de certificados energéticos</h2>
            <p>El organismo encargado de gestionar el registro de CEE en [[{ccaa_slug}]] es:</p>
            <p><strong>[[PENDIENTE]]</strong></p>
            <p>Contacto: [[PENDIENTE]] · [[PENDIENTE]]</p>
            <p><a href="{ccaa_slug}">Más información en organismos-contacto.html</a></p>
        </section>"""

    bloque = f"""        <section class="registro-ccaa">
            <h2>Registro autonómico de certificados energéticos</h2>
            <p>Si necesitas tramitar o consultar el estado de tu certificado energético en <strong>{org['nombre_ccaa']}</strong>, el organismo responsable es:</p>
            <div class="org-data" style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:1rem 1.25rem;margin:.75rem 0">
                <p style="font-weight:700;font-size:1rem;margin-bottom:.5rem">{org['organismo']}</p>
                <p style="font-size:.9rem;color:#4b5563;margin-bottom:.25rem">🌐 <a href="{org['web']}" target="_blank" rel="noopener" style="color:#16a34a">{org['web']}</a></p>
                <p style="font-size:.9rem;color:#4b5563;margin-bottom:.25rem">📞 {org['telefono']}</p>
                <p style="font-size:.9rem;color:#4b5563">✉️ <a href="mailto:{org['email']}" style="color:#16a34a">{org['email']}</a></p>
            </div>
            <p style="font-size:.85rem;color:#6b7280">Para más detalles y el listado completo de organismos, visita nuestra <a href="/organismos-contacto.html" style="color:#16a34a">página de organismos oficiales</a>.</p>
        </section>"""
    return bloque


def inyectar_en_pagina(slug, html_original):
    """
    Inyecta el bloque de registro CCAA ANTES de <footer class="footer-v2">.
    """
    if slug in EXCLUIDAS:
        return None

    bloque = generar_bloque_registro(slug)
    if not bloque:
        return html_original

    html = html_original

    # Insertar ANTES de <footer class="footer-v2">
    footer_marker = '<footer class="footer-v2">'
    if footer_marker in html:
        html = html.replace(footer_marker, bloque + "\n\n        " + footer_marker, 1)
    else:
        print(f"⚠️  {slug}: no se encontró footer marker, probando </body>")
        if "</body>" in html:
            html = html.replace("</body>", bloque + "\n\n    </body>", 1)
        else:
            print(f"❌ {slug}: sin marcador de inserción")
            return None

    return html


def procesar_lote(inicio, fin):
    """Procesa un lote de slugs."""
    # Cargar mapa para tener orden
    map_path = os.path.join(BASE_DIR, "herramientas", "mapa_cercania.json")
    with open(map_path, "r", encoding="utf-8") as f:
        mapa = json.load(f)

    todos_slugs = sorted(mapa.keys())
    lote = [s for s in todos_slugs if s not in EXCLUIDAS][inicio:fin]

    procesados = 0
    errores = []

    for slug in lote:
        dirname = f"certificado-energetico-{slug}"
        indexPath = os.path.join(BASE_DIR, dirname, "index.html")

        if not os.path.isfile(indexPath):
            errores.append(f"{slug}: no existe index.html")
            continue

        with open(indexPath, "r", encoding="utf-8") as f:
            html = f.read()

        html_mod = inyectar_en_pagina(slug, html)
        if html_mod is None:
            errores.append(f"{slug}: error de inyección")
            continue

        with open(indexPath, "w", encoding="utf-8") as f:
            f.write(html_mod)

        procesados += 1
        print(f"✅ {slug} → {PROVINCIA_A_CCAA.get(slug, '?')}")

    return procesados, errores


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) >= 2:
        inicio = int(args[0])
        fin = int(args[1])
    else:
        inicio = 0
        fin = 999

    total, errores = procesar_lote(inicio, fin)

    print(f"\n📊 RESUMEN X2:")
    print(f"   Procesados: {total}")
    print(f"   Errores: {len(errores)}")
    for e in errores:
        print(f"   ⚠️  {e}")

    if total > 0:
        print(f"   ✅ Lote completado")
    else:
        print(f"   ❌ Sin páginas procesadas")
