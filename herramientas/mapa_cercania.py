#!/usr/bin/env python3
"""
Generador de mapa de cercanía para certificadoya.es
Prioriza: mismas CCAA primero, limítrofes después. 6 vecinas por provincia.
Output: herramientas/mapa_cercania.json
"""

import json
import os

# --- Mapeo provincia → CCAA ---
CCAA = {
    "a-coruna": "galicia",
    "alava": "pais-vasco",
    "albacete": "castilla-mancha",
    "alcala-de-henares": "madrid",  # sub-página de Madrid
    "alcobendas": "madrid",
    "alcorcon": "madrid",
    "alicante": "valencia",
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
    "benidorm": "valencia",
    "bilbao": "pais-vasco",
    "bizkaia": "pais-vasco",
    "burgos": "castilla-leon",
    "caceres": "extremadura",
    "cadiz": "andalucia",
    "cantabria": "cantabria",
    "castellon": "valencia",
    "ceuta": "ceuta",
    "chamartin": "madrid",
    "chamberi": "madrid",
    "ciudad-real": "castilla-mancha",
    "cordoba": "andalucia",
    "coruna": "galicia",
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
    "madrid-centro": "madrid",
    "madrid": "madrid",
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
    "salamanca-madrid": "madrid",
    "salamanca": "castilla-leon",
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
    "valencia": "valencia",
    "valladolid": "castilla-leon",
    "venta-vivienda-asturias": "asturias",
    "venta-vivienda-madrid": "madrid",
    "villaviciosa": "asturias",
    "zamora": "castilla-leon",
    "zaragoza": "aragon",
}

# Provincias consideradas principales (no subpáginas de distrito/barrio)
PROVINCIAS_PRINCIPALES = {
    "a-coruna", "alava", "albacete", "alicante", "almeria", "asturias",
    "avila", "badajoz", "baleares", "barcelona", "burgos", "caceres",
    "cadiz", "cantabria", "castellon", "ceuta", "ciudad-real", "cordoba",
    "cuenca", "girona", "granada", "guadalajara", "huelva", "huesca",
    "jaen", "la-rioja", "las-palmas", "leon", "lleida", "lugo", "madrid",
    "malaga", "melilla", "murcia", "navarra", "ourense", "palencia",
    "pontevedra", "salamanca", "segovia", "sevilla", "soria", "tarragona",
    "tenerife", "teruel", "toledo", "valencia", "valladolid", "zamora",
    "zaragoza",
}

# Para subpáginas de ciudad, su provincia "raíz"
SUBPAG_A_PROVINCIA = {
    "alcala-de-henares": "madrid", "alcobendas": "madrid", "alcorcon": "madrid",
    "alquiler-asturias": "asturias", "alquiler-madrid": "madrid",
    "barato-madrid": "madrid", "benidorm": "alicante",
    "bilbao": "bizkaia",  # bilbao es ciudad de vizcaya
    "chamartin": "madrid", "chamberi": "madrid",
    "fuenlabrada": "madrid", "getafe": "madrid",
    "gijon": "asturias", "langreo": "asturias",
    "leganes": "madrid",
    "madrid-centro": "madrid", "mismo-dia-madrid": "madrid",
    "mostoles": "madrid",
    "oviedo": "asturias", "pozuelo": "madrid",
    "precio-asturias": "asturias",
    "retiro": "madrid",
    "salamanca-madrid": "madrid",
    "siero": "asturias",
    "tetuan": "madrid",
    "urgente-asturias": "asturias", "urgente-madrid": "madrid",
    "venta-vivienda-asturias": "asturias", "venta-vivienda-madrid": "madrid",
    "villaviciosa": "asturias",
}

# --- Mapa de vecindad geográfica (provincias limítrofes) ---
# Solo provincias reales (no subpáginas)
VECINOS_GEO = {
    "a-coruna": ["lugo", "pontevedra"],
    "alava": ["bizkaia", "gipuzkoa", "burgos", "la-rioja", "navarra"],
    "albacete": ["ciudad-real", "cuenca", "valencia", "alicante", "murcia", "jaen", "granada"],
    "alicante": ["valencia", "albacete", "murcia"],
    "almeria": ["granada", "murcia"],
    "asturias": ["lugo", "leon", "cantabria"],
    "avila": ["madrid", "segovia", "valladolid", "zamora", "salamanca", "toledo"],
    "badajoz": ["caceres", "ciudad-real", "cordoba", "sevilla", "huelva"],
    "baleares": [],
    "barcelona": ["girona", "lleida", "tarragona"],
    "burgos": ["palencia", "valladolid", "segovia", "soria", "la-rioja", "alava", "cantabria"],
    "caceres": ["badajoz", "ciudad-real", "toledo", "avila", "salamanca"],
    "cadiz": ["sevilla", "malaga", "huelva"],
    "cantabria": ["asturias", "leon", "palencia", "burgos", "bizkaia"],
    "castellon": ["valencia", "teruel", "tarragona"],
    "ceuta": [],
    "ciudad-real": ["badajoz", "caceres", "toledo", "cuenca", "albacete", "jaen", "cordoba"],
    "cordoba": ["sevilla", "badajoz", "ciudad-real", "jaen", "malaga", "granada"],
    "cuenca": ["guadalajara", "madrid", "toledo", "ciudad-real", "albacete", "valencia", "teruel"],
    "girona": ["barcelona", "lleida"],
    "granada": ["jaen", "cordoba", "malaga", "almeria", "murcia", "albacete"],
    "guadalajara": ["madrid", "cuenca", "teruel", "zaragoza", "soria", "segovia"],
    "huelva": ["sevilla", "badajoz", "cadiz"],
    "huesca": ["zaragoza", "lleida", "navarra"],
    "jaen": ["ciudad-real", "albacete", "granada", "cordoba", "murcia"],
    "la-rioja": ["alava", "burgos", "soria", "zaragoza", "navarra"],
    "las-palmas": [],
    "leon": ["asturias", "cantabria", "palencia", "valladolid", "zamora", "ourense", "lugo"],
    "lleida": ["barcelona", "girona", "tarragona", "zaragoza", "huesca"],
    "lugo": ["a-coruna", "pontevedra", "ourense", "leon", "asturias"],
    "madrid": ["avila", "segovia", "guadalajara", "cuenca", "toledo"],
    "malaga": ["cadiz", "sevilla", "cordoba", "granada"],
    "melilla": [],
    "murcia": ["alicante", "albacete", "granada", "almeria"],
    "navarra": ["alava", "gipuzkoa", "la-rioja", "zaragoza", "huesca"],
    "ourense": ["lugo", "pontevedra", "leon", "zamora"],
    "palencia": ["cantabria", "burgos", "valladolid", "leon"],
    "pontevedra": ["a-coruna", "lugo", "ourense"],
    "salamanca": ["zamora", "valladolid", "avila", "caceres"],
    "segovia": ["madrid", "avila", "valladolid", "burgos", "guadalajara", "soria"],
    "sevilla": ["huelva", "badajoz", "cordoba", "malaga", "cadiz"],
    "soria": ["burgos", "la-rioja", "zaragoza", "guadalajara", "segovia"],
    "tarragona": ["barcelona", "lleida", "zaragoza", "teruel", "castellon"],
    "tenerife": [],
    "teruel": ["zaragoza", "tarragona", "castellon", "valencia", "cuenca", "guadalajara"],
    "toledo": ["madrid", "avila", "caceres", "ciudad-real", "cuenca", "guadalajara"],
    "valencia": ["castellon", "teruel", "cuenca", "albacete", "alicante"],
    "valladolid": ["leon", "palencia", "burgos", "segovia", "avila", "zamora", "salamanca"],
    "zamora": ["lugo", "ourense", "leon", "valladolid", "salamanca"],
    "zaragoza": ["huesca", "navarra", "la-rioja", "soria", "guadalajara", "teruel", "tarragona", "lleida"],
}

# Slug → nombre para display
NOMBRES_PROVINCIA = {
    "a-coruna": "A Coruña", "alava": "Álava", "albacete": "Albacete",
    "alcala-de-henares": "Alcalá de Henares", "alcobendas": "Alcobendas",
    "alcorcon": "Alcorcón", "alicante": "Alicante", "almeria": "Almería",
    "alquiler-asturias": "alquiler en Asturias", "alquiler-madrid": "alquiler en Madrid",
    "asturias": "Asturias", "avila": "Ávila", "aviles": "Avilés",
    "badajoz": "Badajoz", "baleares": "Islas Baleares",
    "barato-madrid": "barato en Madrid", "barcelona": "Barcelona",
    "benidorm": "Benidorm", "bilbao": "Bilbao", "bizkaia": "Bizkaia",
    "burgos": "Burgos", "caceres": "Cáceres", "cadiz": "Cádiz",
    "cantabria": "Cantabria", "castellon": "Castellón", "ceuta": "Ceuta",
    "chamartin": "Chamartín", "chamberi": "Chamberí",
    "ciudad-real": "Ciudad Real", "cordoba": "Córdoba", "coruna": "A Coruña",
    "cuenca": "Cuenca", "fuenlabrada": "Fuenlabrada", "getafe": "Getafe",
    "gijon": "Gijón", "gipuzkoa": "Gipuzkoa", "girona": "Girona",
    "granada": "Granada", "guadalajara": "Guadalajara", "huelva": "Huelva",
    "huesca": "Huesca", "jaen": "Jaén", "la-rioja": "La Rioja",
    "langreo": "Langreo", "las-palmas": "Las Palmas", "leganes": "Leganés",
    "leon": "León", "lleida": "Lleida", "lugo": "Lugo",
    "madrid-centro": "Madrid Centro", "madrid": "Madrid",
    "malaga": "Málaga", "melilla": "Melilla", "mismo-dia-madrid": "Madrid mismo día",
    "mostoles": "Móstoles", "murcia": "Murcia", "navarra": "Navarra",
    "ourense": "Ourense", "oviedo": "Oviedo", "palencia": "Palencia",
    "pontevedra": "Pontevedra", "pozuelo": "Pozuelo de Alarcón",
    "precio-asturias": "precio en Asturias", "retiro": "Retiro",
    "salamanca-madrid": "Salamanca (Madrid)", "salamanca": "Salamanca",
    "segovia": "Segovia", "sevilla": "Sevilla", "siero": "Siero",
    "soria": "Soria", "tarragona": "Tarragona", "tenerife": "Tenerife",
    "teruel": "Teruel", "tetuan": "Tetuán", "toledo": "Toledo",
    "urgente-asturias": "urgente en Asturias", "urgente-madrid": "urgente en Madrid",
    "valencia": "Valencia", "valladolid": "Valladolid",
    "venta-vivienda-asturias": "venta de vivienda en Asturias",
    "venta-vivienda-madrid": "venta de vivienda en Madrid",
    "villaviciosa": "Villaviciosa",
    "zamora": "Zamora", "zaragoza": "Zaragoza",
}

# Provincias que son "raíz" para subpáginas (para calcular vecinos)
PROVINCIA_RAIZ = {
    "alcala-de-henares": "madrid", "alcobendas": "madrid", "alcorcon": "madrid",
    "alquiler-asturias": "asturias", "alquiler-madrid": "madrid",
    "barato-madrid": "madrid", "benidorm": "alicante",
    "chamartin": "madrid", "chamberi": "madrid",
    "fuenlabrada": "madrid", "getafe": "madrid",
    "gijon": "asturias", "langreo": "asturias",
    "leganes": "madrid", "madrid-centro": "madrid",
    "mismo-dia-madrid": "madrid", "mostoles": "madrid",
    "oviedo": "asturias", "pozuelo": "madrid",
    "precio-asturias": "asturias", "retiro": "madrid",
    "salamanca-madrid": "madrid", "siero": "asturias",
    "tetuan": "madrid",
    "urgente-asturias": "asturias", "urgente-madrid": "madrid",
    "venta-vivienda-asturias": "asturias", "venta-vivienda-madrid": "madrid",
    "villaviciosa": "asturias",
}


def get_vecinos(slug):
    """
    Devuelve lista de 6 slugs vecinos priorizando:
    1. Misma CCAA (vecinos geográficos de esa CCAA)
    2. CCAA limítrofes
    Para subpáginas: basar en su provincia raíz
    """
    raiz = PROVINCIA_RAIZ.get(slug, slug)
    mi_ccaa = CCAA.get(raiz, "")

    # Primero: vecinos de la misma CCAA
    misma_ccaa = []
    for p in PROVINCIAS_PRINCIPALES:
        if CCAA.get(p) == mi_ccaa and p != raiz and p != "coruna":
            # Ver si son vecinos geográficos o cercanos por CCAA
            if raiz in VECINOS_GEO and p in VECINOS_GEO.get(raiz, []):
                misma_ccaa.append(p)
    
    # Vecinos geográficos (todos)
    vecinos_geo = VECINOS_GEO.get(raiz, [])
    
    # Construir lista completa: mismas CCAA primero, luego limítrofes de otras CCAA
    resultado = []
    
    # Añadir vecinos de misma CCAA
    for v in vecinos_geo:
        if CCAA.get(v) == mi_ccaa and v not in resultado and v != "coruna":
            resultado.append(v)
    
    # Añadir vecinos de otras CCAA
    for v in vecinos_geo:
        if CCAA.get(v) != mi_ccaa and v not in resultado and v != "coruna":
            resultado.append(v)
    
    # Si somos subpágina de Madrid/Asturias, añadir otras provincias principales
    # de la misma CCAA que no sean vecinos directos pero sean de la misma CCAA
    if slug in PROVINCIA_RAIZ or raiz in ("madrid", "asturias"):
        if slug not in PROVINCIAS_PRINCIPALES:  # es subpágina
            # Subpágina de Madrid: añadir otras provincias de Madrid
            otras_misma_ccaa = [p for p in PROVINCIAS_PRINCIPALES 
                               if CCAA.get(p) == mi_ccaa and p != raiz and p != "coruna" and p not in resultado]
            resultado.extend(otras_misma_ccaa[:3])

    # Para provincias sin vecinos (islas, ceuta, melilla), usar provincias de la misma CCAA
    if not resultado:
        otras_misma = [p for p in PROVINCIAS_PRINCIPALES 
                      if CCAA.get(p) == mi_ccaa and p != raiz and p != "coruna"]
        if otras_misma:
            resultado = otras_misma[:6]
        else:
            # Sin vecinos ni misma CCAA: usar principales de España
            todas = sorted(PROVINCIAS_PRINCIPALES - {raiz, "coruna"})
            resultado = todas[:6]

    # Si slug es subpágina, sus vecinos son las mismas provincias de su raíz
    # Pero para el display, se enlazarán a sus rutas reales

    return resultado[:6]


# Generar mapa completo
mapa = {}
for slug in sorted(CCAA.keys()):
    nombre = NOMBRES_PROVINCIA.get(slug, slug)
    ccaa = CCAA.get(slug, "")
    vecinos = get_vecinos(slug)
    vecinos_data = [{"slug": v, "nombre": NOMBRES_PROVINCIA.get(v, v)} for v in vecinos]
    mapa[slug] = {
        "slug": slug,
        "nombre": nombre,
        "ccaa": ccaa,
        "vecinas": vecinos_data
    }

output_path = os.path.join(os.path.dirname(__file__), "mapa_cercania.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(mapa, f, ensure_ascii=False, indent=2)

print(f"✅ Mapa generado: {len(mapa)} entradas")
print(f"   Archivo: {output_path}")
