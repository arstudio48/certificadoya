#!/usr/bin/env python3
"""Genera contenido único para TODAS las landings provinciales de certificadoya.es

Usage:
    python3 generar-contenido-unico.py              # simulación (no escribe)
    python3 generar-contenido-unico.py --apply      # escribe los cambios
"""
import sys, os, re, html as html_mod

BASE = "/home/arturo/certificadoya"
DRY_RUN = "--apply" not in sys.argv

# ============================================================
# DATOS POR PROVINCIA
# ============================================================
province_data = {
    "alava": {"name":"Álava","region":"País Vasco","capital":"Vitoria-Gasteiz","organism":"Ente Vasco de la Energía (EVE)","fee":False,"places":["Vitoria-Gasteiz","Ayala","Llodio","Amurrio","Salvatierra"]},
    "albacete": {"name":"Albacete","region":"Castilla-La Mancha","capital":"Albacete","organism":"Consejería de Desarrollo Sostenible de Castilla-La Mancha","fee":False,"places":["Albacete","Almansa","Hellín","Villarrobledo","La Roda"]},
    "alcala-de-henares": {"name":"Alcalá de Henares","region":"Comunidad de Madrid","capital":"Alcalá de Henares","organism":"Dirección General de Industria, Energía y Minas de la Comunidad de Madrid","fee":False,"places":["Alcalá de Henares","Torrejón de Ardoz","Mejorada del Campo","Villalbilla","Camarma de Esteruelas"]},
    "alcobendas": {"name":"Alcobendas","region":"Comunidad de Madrid","capital":"Alcobendas","organism":"Dirección General de Industria, Energía y Minas de la Comunidad de Madrid","fee":False,"places":["Alcobendas","San Sebastián de los Reyes","Tres Cantos","Colmenar Viejo","Fuente el Saz"]},
    "alcorcon": {"name":"Alcorcón","region":"Comunidad de Madrid","capital":"Alcorcón","organism":"Dirección General de Industria, Energía y Minas de la Comunidad de Madrid","fee":False,"places":["Alcorcón","Móstoles","Fuenlabrada","Leganés","Getafe"]},
    "alicante": {"name":"Alicante","region":"Comunidad Valenciana","capital":"Alicante","organism":"Instituto Valenciano de Competitividad Empresarial (IVACE)","fee":True,"places":["Alicante","Elche","Benidorm","Orihuela","Torrevieja"]},
    "almeria": {"name":"Almería","region":"Andalucía","capital":"Almería","organism":"Consejería de Política Industrial y Energía","fee":False,"places":["Almería","Roquetas de Mar","El Ejido","Níjar","Vera"]},
    "asturias": {"name":"Asturias","region":"Asturias","capital":"Oviedo","organism":"Consejería de Transición Ecológica del Principado de Asturias","fee":False,"places":["Oviedo","Gijón","Avilés","Siero","Mieres"]},
    "avila": {"name":"Ávila","region":"Castilla y León","capital":"Ávila","organism":"Consejería de Industria de la Junta de Castilla y León","fee":False,"places":["Ávila","Arévalo","Piedrahíta","Barco de Ávila","Cebreros"]},
    "badajoz": {"name":"Badajoz","region":"Extremadura","capital":"Badajoz","organism":"Dirección General de Industria, Energía y Minas de la Junta de Extremadura","fee":False,"places":["Badajoz","Mérida","Don Benito","Almendralejo","Villanueva de la Serena"]},
    "baleares": {"name":"Baleares","region":"Islas Baleares","capital":"Palma","organism":"Direcció General d'Energia i Canvi Climàtic","fee":True,"places":["Palma de Mallorca","Ibiza","Manacor","Mahón","Calvià"]},
    "barcelona": {"name":"Barcelona","region":"Cataluña","capital":"Barcelona","organism":"Institut Català d'Energia (ICAEN)","fee":True,"places":["Barcelona","Badalona","L'Hospitalet","Sabadell","Terrassa"]},
    "bilbao": {"name":"Bilbao","region":"País Vasco","capital":"Bilbao","organism":"Ente Vasco de la Energía (EVE)","fee":False,"places":["Bilbao","Barakaldo","Getxo","Santurtzi","Portugalete"]},
    "burgos": {"name":"Burgos","region":"Castilla y León","capital":"Burgos","organism":"Consejería de Industria de la Junta de Castilla y León","fee":False,"places":["Burgos","Miranda de Ebro","Aranda de Duero","Briviesca","Villarcayo"]},
    "caceres": {"name":"Cáceres","region":"Extremadura","capital":"Cáceres","organism":"Dirección General de Industria, Energía y Minas de la Junta de Extremadura","fee":False,"places":["Cáceres","Plasencia","Navalmoral de la Mata","Coria","Trujillo"]},
    "cadiz": {"name":"Cádiz","region":"Andalucía","capital":"Cádiz","organism":"Consejería de Política Industrial y Energía","fee":False,"places":["Cádiz","Jerez de la Frontera","Algeciras","San Fernando","Chiclana"]},
    "cantabria": {"name":"Cantabria","region":"Cantabria","capital":"Santander","organism":"Dirección General de Industria del Gobierno de Cantabria","fee":False,"places":["Santander","Torrelavega","Castro Urdiales","Laredo","Santoña"]},
    "castellon": {"name":"Castellón","region":"Comunidad Valenciana","capital":"Castellón","organism":"IVACE","fee":True,"places":["Castellón de la Plana","Vila-real","Borriana","La Vall d'Uixó","Benicarló"]},
    "ceuta": {"name":"Ceuta","region":"Ceuta","capital":"Ceuta","organism":"Consejería de Fomento","fee":False,"places":["Ceuta"]},
    "ciudad-real": {"name":"Ciudad Real","region":"Castilla-La Mancha","capital":"Ciudad Real","organism":"Consejería de Desarrollo Sostenible de Castilla-La Mancha","fee":False,"places":["Ciudad Real","Puertollano","Tomelloso","Alcázar de San Juan","Valdepeñas"]},
    "cordoba": {"name":"Córdoba","region":"Andalucía","capital":"Córdoba","organism":"Consejería de Política Industrial y Energía","fee":False,"places":["Córdoba","Lucena","Puente Genil","Montilla","Palma del Río"]},
    "coruna": {"name":"A Coruña","region":"Galicia","capital":"A Coruña","organism":"INEGA","fee":False,"places":["A Coruña","Santiago","Ferrol","Arteixo","Carballo"]},
    "cuenca": {"name":"Cuenca","region":"Castilla-La Mancha","capital":"Cuenca","organism":"Consejería de Desarrollo Sostenible","fee":False,"places":["Cuenca","Tarancón","San Clemente","Las Pedroñeras","Mota del Cuervo"]},
    "fuenlabrada": {"name":"Fuenlabrada","region":"Comunidad de Madrid","capital":"Fuenlabrada","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Fuenlabrada","Móstoles","Leganés","Getafe","Pinto"]},
    "getafe": {"name":"Getafe","region":"Comunidad de Madrid","capital":"Getafe","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Getafe","Leganés","Fuenlabrada","Pinto","Parla"]},
    "gijon": {"name":"Gijón","region":"Asturias","capital":"Gijón","organism":"Consejería de Transición Ecológica de Asturias","fee":False,"places":["Gijón","Villaviciosa","Carreño","Siero","Sariego"]},
    "gipuzkoa": {"name":"Gipuzkoa","region":"País Vasco","capital":"San Sebastián","organism":"Ente Vasco de la Energía (EVE)","fee":False,"places":["Donostia-San Sebastián","Irún","Rentería","Eibar","Zarauz"]},
    "girona": {"name":"Girona","region":"Cataluña","capital":"Girona","organism":"ICAEN","fee":True,"places":["Girona","Figueres","Blanes","Lloret de Mar","Olot"]},
    "granada": {"name":"Granada","region":"Andalucía","capital":"Granada","organism":"Consejería de Política Industrial y Energía","fee":False,"places":["Granada","Motril","Almuñécar","Armilla","Maracena"]},
    "guadalajara": {"name":"Guadalajara","region":"Castilla-La Mancha","capital":"Guadalajara","organism":"Consejería de Desarrollo Sostenible","fee":False,"places":["Guadalajara","Azuqueca de Henares","Sigüenza","Molina de Aragón","Pastrana"]},
    "huelva": {"name":"Huelva","region":"Andalucía","capital":"Huelva","organism":"Consejería de Política Industrial y Energía","fee":False,"places":["Huelva","Lepe","Isla Cristina","Ayamonte","Almonte"]},
    "huesca": {"name":"Huesca","region":"Aragón","capital":"Huesca","organism":"INAGA","fee":False,"places":["Huesca","Jaca","Monzón","Barbastro","Fraga"]},
    "jaen": {"name":"Jaén","region":"Andalucía","capital":"Jaén","organism":"Consejería de Política Industrial y Energía","fee":False,"places":["Jaén","Linares","Úbeda","Andújar","Martos"]},
    "la-rioja": {"name":"La Rioja","region":"La Rioja","capital":"Logroño","organism":"Dirección General de Transición Energética de La Rioja","fee":False,"places":["Logroño","Calahorra","Arnedo","Haro","Alfaro"]},
    "langreo": {"name":"Langreo","region":"Asturias","capital":"Langreo","organism":"Consejería de Transición Ecológica de Asturias","fee":False,"places":["Langreo","Siero","Mieres","Laviana","San Martín del Rey Aurelio"]},
    "las-palmas": {"name":"Las Palmas","region":"Canarias","capital":"Las Palmas de GC","organism":"Consejería de Transición Ecológica de Canarias","fee":False,"places":["Las Palmas de Gran Canaria","Telde","Santa Lucía","Arucas","San Bartolomé de Tirajana"]},
    "leganes": {"name":"Leganés","region":"Comunidad de Madrid","capital":"Leganés","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Leganés","Getafe","Alcorcón","Fuenlabrada","Villaverde"]},
    "leon": {"name":"León","region":"Castilla y León","capital":"León","organism":"Consejería de Industria de la Junta de Castilla y León","fee":False,"places":["León","Ponferrada","Astorga","La Bañeza","San Andrés del Rabanedo"]},
    "lleida": {"name":"Lleida","region":"Cataluña","capital":"Lleida","organism":"ICAEN","fee":True,"places":["Lleida","Tàrrega","Balaguer","La Seu d'Urgell","Mollerussa"]},
    "lugo": {"name":"Lugo","region":"Galicia","capital":"Lugo","organism":"INEGA","fee":False,"places":["Lugo","Monforte de Lemos","Viveiro","Ribadeo","Sarria"]},
    "malaga": {"name":"Málaga","region":"Andalucía","capital":"Málaga","organism":"Consejería de Política Industrial y Energía","fee":False,"places":["Málaga","Marbella","Fuengirola","Torremolinos","Benalmádena"]},
    "melilla": {"name":"Melilla","region":"Melilla","capital":"Melilla","organism":"Consejería de Medio Ambiente de Melilla","fee":False,"places":["Melilla"]},
    "murcia": {"name":"Murcia","region":"Región de Murcia","capital":"Murcia","organism":"Dirección General de Energía de la Región de Murcia","fee":False,"places":["Murcia","Cartagena","Lorca","Molina de Segura","Alcantarilla"]},
    "navarra": {"name":"Navarra","region":"Navarra","capital":"Pamplona","organism":"Dirección General de Industria y Energía de Navarra","fee":False,"places":["Pamplona","Tudela","Estella","Tafalla","Burlada"]},
    "ourense": {"name":"Ourense","region":"Galicia","capital":"Ourense","organism":"INEGA","fee":False,"places":["Ourense","Verín","O Barco de Valdeorras","Xinzo de Limia","Celanova"]},
    "palencia": {"name":"Palencia","region":"Castilla y León","capital":"Palencia","organism":"Consejería de Industria de la Junta de Castilla y León","fee":False,"places":["Palencia","Guardo","Aguilar de Campoo","Venta de Baños","Saldaña"]},
    "pontevedra": {"name":"Pontevedra","region":"Galicia","capital":"Pontevedra","organism":"INEGA","fee":False,"places":["Pontevedra","Vigo","Marín","Vilagarcía de Arousa","Redondela"]},
    "salamanca": {"name":"Salamanca","region":"Castilla y León","capital":"Salamanca","organism":"Consejería de Industria de la Junta de Castilla y León","fee":False,"places":["Salamanca","Béjar","Ciudad Rodrigo","Santa Marta de Tormes","Villares de la Reina"]},
    "segovia": {"name":"Segovia","region":"Castilla y León","capital":"Segovia","organism":"Consejería de Industria de la Junta de Castilla y León","fee":False,"places":["Segovia","Cuéllar","Sepúlveda","La Granja","Riaza"]},
    "sevilla": {"name":"Sevilla","region":"Andalucía","capital":"Sevilla","organism":"Consejería de Política Industrial y Energía","fee":False,"places":["Sevilla","Dos Hermanas","Alcalá de Guadaíra","Mairena del Aljarafe","Écija"]},
    "soria": {"name":"Soria","region":"Castilla y León","capital":"Soria","organism":"Consejería de Industria de la Junta de Castilla y León","fee":False,"places":["Soria","Almazán","Burgo de Osma","Ágreda","San Esteban de Gormaz"]},
    "tarragona": {"name":"Tarragona","region":"Cataluña","capital":"Tarragona","organism":"ICAEN","fee":True,"places":["Tarragona","Reus","Tortosa","Salou","Vendrell"]},
    "tenerife": {"name":"Tenerife","region":"Canarias","capital":"Santa Cruz de Tenerife","organism":"Consejería de Transición Ecológica de Canarias","fee":False,"places":["Santa Cruz de Tenerife","La Laguna","Arona","La Orotava","Adeje"]},
    "teruel": {"name":"Teruel","region":"Aragón","capital":"Teruel","organism":"INAGA","fee":False,"places":["Teruel","Alcañiz","Andorra","Calamocha","Montalbán"]},
    "toledo": {"name":"Toledo","region":"Castilla-La Mancha","capital":"Toledo","organism":"Consejería de Desarrollo Sostenible","fee":False,"places":["Toledo","Talavera de la Reina","Illescas","Sonseca","Madridejos"]},
    "valencia": {"name":"Valencia","region":"Comunidad Valenciana","capital":"Valencia","organism":"IVACE","fee":True,"places":["Valencia","Torrent","Gandía","Paterna","Sagunto"]},
    "valladolid": {"name":"Valladolid","region":"Castilla y León","capital":"Valladolid","organism":"Consejería de Industria de la Junta de Castilla y León","fee":False,"places":["Valladolid","Medina del Campo","Laguna de Duero","Peñafiel","Tordesillas"]},
    "zamora": {"name":"Zamora","region":"Castilla y León","capital":"Zamora","organism":"Consejería de Industria de la Junta de Castilla y León","fee":False,"places":["Zamora","Benavente","Toro","San Cristóbal de Entreviñas","Morales del Vino"]},
    "zaragoza": {"name":"Zaragoza","region":"Aragón","capital":"Zaragoza","organism":"INAGA","fee":False,"places":["Zaragoza","Calatayud","Épila","Utebo","Tarazona"]},
    # Madrid special cases
    "alquiler-madrid": {"name":"alquiler en Madrid","region":"Comunidad de Madrid","capital":"Madrid","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Madrid capital","Alcobendas","Móstoles","Alcalá de Henares","Fuenlabrada"]},
    "alquiler-asturias": {"name":"alquiler en Asturias","region":"Asturias","capital":"Oviedo","organism":"Consejería de Transición Ecológica de Asturias","fee":False,"places":["Oviedo","Gijón","Avilés","Siero","Langreo"]},
    "a-coruna": {"name":"A Coruña","region":"Galicia","capital":"A Coruña","organism":"INEGA","fee":False,"places":["A Coruña","Santiago","Ferrol","Arteixo","Narón"]},
    "aviles": {"name":"Avilés","region":"Asturias","capital":"Avilés","organism":"Consejería de Transición Ecológica de Asturias","fee":False,"places":["Avilés","Corvera","Castrillón","Gozón","Illas"]},
    "barato-madrid": {"name":"barato en Madrid","region":"Comunidad de Madrid","capital":"Madrid","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Madrid capital","Leganés","Getafe","Móstoles","Alcorcón"]},
    "benidorm": {"name":"Benidorm","region":"Comunidad Valenciana","capital":"Benidorm","organism":"IVACE","fee":True,"places":["Benidorm","La Vila Joiosa","l'Alfàs del Pi","Callosa d'en Sarrià","Polop"]},
    "bizkaia": {"name":"Bizkaia","region":"País Vasco","capital":"Bilbao","organism":"EVE","fee":False,"places":["Bilbao","Barakaldo","Getxo","Durango","Bermeo"]},
    "chamartin": {"name":"Chamartín","region":"Comunidad de Madrid","capital":"Madrid","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Chamartín","Tetuán","Chamberí","Salamanca","Ciudad Lineal"]},
    "chamberi": {"name":"Chamberí","region":"Comunidad de Madrid","capital":"Madrid","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Chamberí","Chamartín","Salamanca","Centro","Tetuán"]},
    "madrid-centro": {"name":"Madrid Centro","region":"Comunidad de Madrid","capital":"Madrid","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Centro","Salamanca","Chamberí","Retiro","Arganzuela"]},
    "mieres": {"name":"Mieres","region":"Asturias","capital":"Mieres","organism":"Consejería de Transición Ecológica de Asturias","fee":False,"places":["Mieres","Langreo","Laviana","Aller","San Martín del Rey Aurelio"]},
    "mismo-dia-madrid": {"name":"mismo día en Madrid","region":"Comunidad de Madrid","capital":"Madrid","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Madrid"]},
    "mostoles": {"name":"Móstoles","region":"Comunidad de Madrid","capital":"Móstoles","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Móstoles","Alcorcón","Fuenlabrada","Navalcarnero","Arroyomolinos"]},
    "oviedo": {"name":"Oviedo","region":"Asturias","capital":"Oviedo","organism":"Consejería de Transición Ecológica de Asturias","fee":False,"places":["Oviedo","Siero","Llanera","Grado","Ribera de Arriba"]},
    "pozuelo": {"name":"Pozuelo de Alarcón","region":"Comunidad de Madrid","capital":"Pozuelo","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Pozuelo de Alarcón","Majadahonda","Las Rozas","Boadilla del Monte","Aravaca"]},
    "precio-asturias": {"name":"precio en Asturias","region":"Asturias","capital":"Oviedo","organism":"Consejería de Transición Ecológica de Asturias","fee":False,"places":["Oviedo","Gijón","Avilés","Siero","Langreo"]},
    "retiro": {"name":"Retiro","region":"Comunidad de Madrid","capital":"Madrid","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Retiro","Salamanca","Puente de Vallecas","Moratalaz","Pacífico"]},
    "salamanca-madrid": {"name":"Salamanca (barrio)","region":"Comunidad de Madrid","capital":"Madrid","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Salamanca","Chamartín","Retiro","Chamberí","Centro"]},
    "siero": {"name":"Siero","region":"Asturias","capital":"Pola de Siero","organism":"Consejería de Transición Ecológica de Asturias","fee":False,"places":["Pola de Siero","Oviedo","Gijón","Langreo","Nava"]},
    "tetuan": {"name":"Tetuán","region":"Comunidad de Madrid","capital":"Madrid","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Tetuán","Chamartín","Chamberí","Fuencarral","Moncloa"]},
    "urgente-madrid": {"name":"urgente en Madrid","region":"Comunidad de Madrid","capital":"Madrid","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Madrid capital","Alcobendas","Las Rozas","Pozuelo","Majadahonda"]},
    "urgente-asturias": {"name":"urgente en Asturias","region":"Asturias","capital":"Oviedo","organism":"Consejería de Transición Ecológica de Asturias","fee":False,"places":["Oviedo","Gijón","Avilés","Siero","Langreo"]},
    "venta-vivienda-madrid": {"name":"venta en Madrid","region":"Comunidad de Madrid","capital":"Madrid","organism":"Comunidad de Madrid (Energía)","fee":False,"places":["Madrid capital","Alcobendas","Las Rozas","Pozuelo","Majadahonda"]},
    "venta-vivienda-asturias": {"name":"venta en Asturias","region":"Asturias","capital":"Oviedo","organism":"Consejería de Transición Ecológica de Asturias","fee":False,"places":["Oviedo","Gijón","Avilés","Siero","Langreo"]},
    "villaviciosa": {"name":"Villaviciosa","region":"Asturias","capital":"Villaviciosa","organism":"Consejería de Transición Ecológica de Asturias","fee":False,"places":["Villaviciosa","Gijón","Colunga","Sariego","Cabranes"]},
}

PLACES_KEY = {
    "a-coruna": "a-coruna2",
}

# Títulos únicos por provincia
def gen_title(d, p):
    name_lower = p["name"].lower()
    if p["fee"]:
        suffix = "precios actualizados"
    else:
        suffix = "precios actualizados"
    return f"🏠 Certificado Energético {p['name']} desde 45€ — CEE oficial {suffix}"

def gen_meta_desc(d, p):
    places_str = ", ".join(p["places"][:3])
    return f"Certificado de eficiencia energética (CEE) en {p['name']}. Presupuesto instantáneo en {places_str}. Técnicos colegiados. Desde 45€. Resultado en 48h."

def gen_og_title(d, p):
    return f"🏠 CEE {p['name']} — Precios y trámites 2026 desde 45€"

# Contenido único del content-section
def gen_content_section(d, p):
    name = p["name"]
    region = p["region"]
    cap = p["capital"]
    org = p["organism"]
    fee = p["fee"]
    places = p["places"]
    p2 = ", ".join(places[:2])
    p3 = ", ".join(places[:3])
    
    fee_text = "El coste del registro puede variar según la normativa vigente de cada comunidad autónoma. En CertificadoYa te informamos del importe exacto antes de confirmar el servicio."
    
    h2s = [
        f"Certificado energético en {name}: todo lo que necesitas saber",
        f"CEE en {name}: precios, plazos y registro oficial",
        f"Tu certificado energético en {name}, fácil y rápido",
        f"Certificado de eficiencia energética en {name} — guía completa",
        f"¿Necesitas el CEE en {name}? Descubre cómo obtenerlo"
    ]
    h2 = h2s[hash(d) % len(h2s)]
    
    intro_paragraphs = [
        f"Si vives en {name} o tienes una propiedad en esta zona, necesitarás el <strong>certificado de eficiencia energética (CEE)</strong> para vender o alquilar tu inmueble. En CertificadoYa te ofrecemos un servicio completo con técnicos colegiados en toda el área de {p2}, presupuestos transparentes y registro oficial incluido. Desde 45€ para un piso estándar, con resultado en 48 horas.",
        f"Tanto si tu propiedad está en el centro de {cap} como si se encuentra en una de las localidades cercanas como {p3}, nuestro servicio de certificación energética cubre toda la zona de {name}. Contamos con técnicos colegiados que conocen las particularidades de la región y los requisitos del organismo autonómico.",
    ]
    intro = intro_paragraphs[hash(d + "intro") % len(intro_paragraphs)]
    
    precio_texts = [
        f"Los precios del certificado energético en {name} varían según los metros cuadrados, el tipo de inmueble y su ubicación exacta. Todos nuestros presupuestos incluyen la visita del técnico, la emisión con software oficial y el registro en el organismo correspondiente.",
        f"El coste del CEE en {name} depende principalmente de la superficie del inmueble. En CertificadoYa te damos el precio exacto al instante con nuestra calculadora online. Sin compromiso y sin esperas.",
    ]
    precio_text = precio_texts[hash(d + "precio") % len(precio_texts)]
    
    confianza = [
        f"<li><strong>Técnicos colegiados en {name}</strong>: profesionales verificados que conocen la zona</li>",
        f"<li><strong>Conocimiento local</strong>: nuestros técnicos trabajan habitualmente en {name} y sus alrededores</li>",
    ]
    conf = confianza[hash(d + "conf") % len(confianza)]
    
    faq_precio_q = f"¿Cuánto cuesta el certificado energético en {name}?"
    faq_precio_a = f"El precio en {name} oscila entre <strong>45€ y 85€</strong> para un piso de 50-70 m², y entre <strong>85€ y 130€</strong> para uno de 70-100 m². Las viviendas unifamiliares y locales tienen tarifas distintas. Usa nuestra calculadora gratuita para el precio exacto según tu código postal."
    
    faq_organismo_q = f"¿Quién regula el CEE en {name}?"
    faq_organismo_a = f"El organismo competente en {region} es {org}. El registro se realiza de forma telemática a través de su sede electrónica. {fee_text}"
    
    return f"""  <section class="content-section">

    <h2>{h2}</h2>
    <p>{intro}</p>

    <details class="accordion-section" open>
    <summary>📊 Precios del certificado energético en {name} por superficie</summary>
    <div class="accordion-body">
    <p>{precio_text}</p>

    <table class="tabla-precios">
      <thead>
        <tr><th>Tipo de inmueble</th><th>Superficie</th><th>Precio orientativo</th></tr>
      </thead>
      <tbody>
        <tr><td>Piso / Apartamento</td><td>50 — 70 m²</td><td><strong>45 — 75 €</strong></td></tr>
        <tr><td>Piso / Apartamento</td><td>70 — 100 m²</td><td><strong>75 — 110 €</strong></td></tr>
        <tr><td>Piso / Apartamento</td><td>100 — 150 m²</td><td><strong>110 — 150 €</strong></td></tr>
        <tr><td>Unifamiliar / Chalet</td><td>100 — 150 m²</td><td><strong>130 — 170 €</strong></td></tr>
        <tr><td>Unifamiliar / Chalet</td><td>150 — 250 m²</td><td><strong>170 — 240 €</strong></td></tr>
        <tr><td>Adosado / Pareado</td><td>80 — 120 m²</td><td><strong>95 — 135 €</strong></td></tr>
        <tr><td>Local comercial</td><td>50 — 150 m²</td><td><strong>65 — 140 €</strong></td></tr>
        <tr><td>Oficina / Despacho</td><td>50 — 100 m²</td><td><strong>70 — 110 €</strong></td></tr>
      </tbody>
    </table>
    <p style="font-size:.82rem;color:var(--gray-600)">* Precios orientativos a junio de 2026. El presupuesto final depende de la ubicación exacta y las características del inmueble.</p>
  </div>
</details>

    <details class="accordion-section">
    <summary>🏛️ Organismo competente en {region}</summary>
    <div class="accordion-body">
    <p>El registro de los certificados de eficiencia energética en {region} se realiza a través de <strong>{org}</strong>.</p>
    <ul>
      <li><strong>Organismo:</strong> {org}</li>
      <li><strong>Registro telemático:</strong> A través de la sede electrónica del organismo autonómico</li>
      <li><strong>Localización:</strong> {cap} ({region})</li>
      <li><strong>Tasas:</strong> {'Sí, existe una tasa autonómica de registro' if fee else 'No hay tasa autonómica para el registro del CEE'}</li>
    </ul>
    <p>{fee_text}</p>
  </div>
</details>

    <details class="accordion-section">
    <summary>⏱️ Plazos del proceso en {name}</summary>
    <div class="accordion-body">
    <ol>
      <li><strong>Visita técnica:</strong> 24 — 48h desde la confirmación del presupuesto (el técnico acuerda contigo la cita)</li>
      <li><strong>Cálculo y emisión:</strong> 24 — 48h tras la visita (software oficial CE3X / CYPETHERM / HULC)</li>
      <li><strong>Registro oficial:</strong> 7 — 15 días hábiles desde la presentación telemática en el organismo autonómico</li>
    </ol>
    <p>Para vender o alquilar, con el certificado emitido y en proceso de registro ya es suficiente legalmente.</p>
  </div>
</details>

    <details class="accordion-section">
    <summary>✅ ¿Por qué elegir CertificadoYa en {name}?</summary>
    <div class="accordion-body">
    <ul>
      {conf}
      <li><strong>Presupuesto al instante</strong>: sabes el precio exacto antes de comprometerte</li>
      <li><strong>Precio cerrado</strong>: sin sorpresas ni costes ocultos</li>
      <li><strong>Certificado registrado</strong>: nos encargamos de todo el trámite con el organismo oficial</li>
      <li><strong>Atención local</strong>: conocemos las particularidades de {name} y {region}</li>
    </ul>
  </div>
</details>

    <details class="accordion-section">
    <summary>❓ Preguntas frecuentes sobre el CEE en {name}</summary>
    <div class="accordion-body">

    <details class="faq-item">
      <summary class="faq-question">{faq_precio_q}</summary>
      <div class="faq-answer"><p>{faq_precio_a}</p></div>
    </details>

    <details class="faq-item">
      <summary class="faq-question">{faq_organismo_q}</summary>
      <div class="faq-answer"><p>{faq_organismo_a}</p></div>
    </details>

    <details class="faq-item">
      <summary class="faq-question">¿En cuánto tiempo tengo el certificado en {name}?</summary>
      <div class="faq-answer"><p>El proceso completo dura <strong>48-72 horas</strong> para la visita técnica, y el certificado se entrega en las siguientes 24-48 horas. El registro oficial puede demorar entre 7 y 15 días hábiles, pero con el certificado emitido ya puedes vender o alquilar legalmente.</p></div>
    </details>

    <details class="faq-item">
      <summary class="faq-question">¿El certificado de {name} vale en toda España?</summary>
      <div class="faq-answer"><p>Sí, el certificado de eficiencia energética (CEE) emitido por un técnico colegiado tiene validez en todo el territorio nacional, independientemente de la comunidad autónoma donde se registre. Su validez es de <strong>10 años</strong> para viviendas de hasta 1.000 m².</p></div>
    </details>

  </div>
</details>

  </section>"""

# ============================================================
# PROCESAR CADA LANDING
# ============================================================
import glob

dirs = sorted(os.listdir(BASE))
landings = [d for d in dirs if d.startswith("certificado-energetico-") and os.path.isdir(os.path.join(BASE, d))]
print(f"Landings encontradas: {len(landings)}")

stats = {"ok": 0, "saltado": 0, "error": 0}

for ld in landings:
    dir_name = ld.replace("certificado-energetico-", "")
    if dir_name not in province_data:
        # Try truncated match
        matched = [k for k in province_data if dir_name.startswith(k) or k.startswith(dir_name)]
        if matched:
            dir_name = matched[0]
        else:
            print(f"  ⚠️  SALTADO: {ld} — no hay datos para '{dir_name}'")
            stats["saltado"] += 1
            continue
    
    p = province_data[dir_name]
    fpath = os.path.join(BASE, ld, "index.html")
    
    if not os.path.exists(fpath):
        print(f"  ⚠️  SALTADO: {ld}/index.html no existe")
        stats["saltado"] += 1
        continue
    
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
    
    changes = 0
    # 1. Title
    new_title = gen_title(dir_name, p)
    old_title_match = re.search(r'<title>(.*?)</title>', html)
    if old_title_match:
        old_t = old_title_match.group(1)
        if "desde 60" in old_t or old_t != new_title:
            html = html.replace(old_t, new_title, 1)
            changes += 1
    
    # 2. Meta description
    new_meta = gen_meta_desc(dir_name, p)
    old_desc_match = re.search(r'<meta name="description" content="(.*?)">', html)
    if old_desc_match:
        old_d = old_desc_match.group(1)
        if "desde 60" in old_d or old_d != new_meta:
            html = html.replace(old_desc_match.group(0), f'<meta name="description" content="{new_meta}">', 1)
            changes += 1
    
    # 3. og:title
    new_og = gen_og_title(dir_name, p)
    og_match = re.search(r'<meta property="og:title" content="(.*?)">', html)
    if og_match:
        old_og = og_match.group(1)
        if "60€" in old_og or old_og != new_og:
            html = html.replace(og_match.group(0), f'<meta property="og:title" content="{new_og}">', 1)
            changes += 1
    
    # 4. og:description
    og_desc_match = re.search(r'<meta property="og:description" content="(.*?)">', html)
    if og_desc_match and "60€" in og_desc_match.group(1):
        new_og_desc = f"Emisión y registro del CEE oficial en {p['name']}. Técnico colegiado, presupuesto desde 45€."
        html = html.replace(og_desc_match.group(0), f'<meta property="og:description" content="{new_og_desc}">', 1)
        changes += 1
    
    # 5. twitter:title
    tw_match = re.search(r'<meta name="twitter:title" content="(.*?)">', html)
    if tw_match and "60€" in tw_match.group(1):
        new_tw = f"🏠 CEE {p['name']} — Desde 45€"
        html = html.replace(tw_match.group(0), f'<meta name="twitter:title" content="{new_tw}">', 1)
        changes += 1
    
    # 6. twitter:description
    twd_match = re.search(r'<meta name="twitter:description" content="(.*?)">', html)
    if twd_match and "60€" in twd_match.group(1):
        new_twd = f"Técnicos verificados en {p['name']}. Presupuesto al instante."
        html = html.replace(twd_match.group(0), f'<meta name="twitter:description" content="{new_twd}">', 1)
        changes += 1
    
    # 7. JSON-LD description
    json_ld_match = re.search(r'"description":\s*"([^"]*desde 60[^"]*)"', html)
    if json_ld_match:
        new_jd = f"Emisión y registro del CEE oficial en {p['name']}. Técnico colegiado, presupuesto desde 45€."
        html = html.replace(json_ld_match.group(0), f'"description": "{new_jd}"', 1)
        changes += 1
    
    # 8. Reemplazar el content-section completo si no tiene accordion
    if "accordion-section" not in html and "content-section" in html:
        new_content = gen_content_section(dir_name, p)
        # Find the old content-section block
        cs_match = re.search(r'<section class="content-section">.*?</section>', html, re.DOTALL)
        if cs_match:
            html = html.replace(cs_match.group(0), new_content, 1)
            changes += 10  # big change
    
    # 9. footer price
    html = html.replace('desde 60€', 'desde 45€')
    
    if DRY_RUN:
        if changes > 0:
            print(f"  📝 {ld}: {changes} cambio(s) pendiente(s) (simulación)")
            stats["ok"] += 1
        else:
            print(f"  ✅ {ld}: sin cambios necesarios")
            stats["saltado"] += 1
    else:
        if changes > 0:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  ✅ {ld}: {changes} cambio(s) aplicados")
            stats["ok"] += 1
        else:
            print(f"  ⏭️  {ld}: sin cambios necesarios")
            stats["saltado"] += 1

print(f"\n{'='*50}")
print(f"Resumen: {stats['ok']} modificadas, {stats['saltado']} sin cambios, {stats['error']} errores")
if DRY_RUN:
    print("\n⚠️  MODO SIMULACIÓN — usa --apply para escribir los cambios")
