#!/usr/bin/env python3
"""
x1_inyectar_interlinking.py — Inyecta bloque de provincias cercanas + enlaces a blog
en landing pages provinciales de certificadoya.es.

Dos inserciones:
1. Bloque <section class="provincias-cercanas"> con 6 enlaces a provincias vecinas
   → ANTES de <footer class="footer-v2">
2. Enlaces a artículos del blog tras el primer <h2>
   → TRAS el primer <h2>

Usa mapa_cercania.json para datos de vecindad.
"""

import json
import os
import re
import sys

# Directorio raíz del proyecto
BASE_DIR = "/home/arturo/certificadoya"
MAP_PATH = os.path.join(BASE_DIR, "herramientas", "mapa_cercania.json")
EXCLUIDAS = {"coruna"}  # stub redirect (redirige a a-coruna)

# Cargar mapa de cercanía
with open(MAP_PATH, "r", encoding="utf-8") as f:
    mapa = json.load(f)

# Provincias que son subpáginas de Madrid - usan slug limpio para enlazar
SUBPAG_MADRID = {
    "alcala-de-henares", "alcobendas", "alcorcon", "barato-madrid",
    "chamartin", "chamberi", "fuenlabrada", "getafe", "leganes",
    "madrid-centro", "mismo-dia-madrid", "mostoles", "pozuelo",
    "retiro", "salamanca-madrid", "tetuan", "urgente-madrid",
    "alquiler-madrid", "venta-vivienda-madrid"
}
SUBPAG_ASTURIAS = {
    "aviles", "gijon", "langreo", "oviedo", "siero",
    "villaviciosa", "alquiler-asturias", "precio-asturias",
    "urgente-asturias", "venta-vivienda-asturias"
}
SUBPAG_BIZKAIA = {"bilbao"}

def es_subpagina(slug):
    """Verifica si un slug es subpágina de una provincia principal"""
    return slug in SUBPAG_MADRID or slug in SUBPAG_ASTURIAS or slug in SUBPAG_BIZKAIA

def ruta_enlace(vecino_slug):
    """Genera la ruta correcta para enlazar a una provincia vecina"""
    # Si es una provincia principal
    dirname = f"certificado-energetico-{vecino_slug}"
    if os.path.isdir(os.path.join(BASE_DIR, dirname)):
        return f"/{dirname}/"
    return None

def generar_bloque_vecinos(slug):
    """Genera el HTML del bloque de provincias cercanas"""
    entrada = mapa.get(slug)
    if not entrada:
        return None
    
    vecinas = entrada.get("vecinas", [])
    if not vecinas:
        return None
    
    enlaces = []
    for v in vecinas:
        ruta = ruta_enlace(v["slug"])
        if ruta:
            enlaces.append(f'                <li><a href="{ruta}">{v["nombre"]}</a></li>')
    
    if not enlaces:
        return None
    
    enlaces_html = "\n".join(enlaces)
    bloque = f"""        <section class="provincias-cercanas">
            <h2>Provincias cercanas</h2>
            <p>Si necesitas un certificado energético en alguna de estas zonas, visita nuestras páginas específicas:</p>
            <ul>
{enlaces_html}
            </ul>
        </section>"""
    return bloque


def generar_bloque_blog():
    """Genera el HTML del bloque de enlaces al blog"""
    return """        <section class="enlaces-blog">
            <h2>Artículos relacionados en el blog</h2>
            <ul>
                <li><a href="/blog/como-elegir-un-certificado-energetico-de-confianza/">Cómo elegir un certificado energético de confianza</a></li>
                <li><a href="/blog/que-es-el-certificado-energetico-y-por-que-es-obligatorio/">Qué es el certificado energético y por qué es obligatorio</a></li>
                <li><a href="/blog/precio-del-certificado-energetico-en-espana/">Precio del certificado energético en España</a></li>
                <li><a href="/blog/">Ver todos los artículos del blog</a></li>
            </ul>
        </section>"""


def inyectar_en_pagina(slug, html_original):
    """
    Inyecta los bloques en el HTML.
    Retorna el HTML modificado o None si no se pudo.
    """
    if slug in EXCLUIDAS:
        return None
    
    bloque_vecinos = generar_bloque_vecinos(slug)
    bloque_blog = generar_bloque_blog()
    
    if not bloque_vecinos:
        return html_original
    
    html = html_original
    
    # --- 1. Insertar bloque de vecinos ANTES de <footer class="footer-v2"> ---
    footer_marker = '<footer class="footer-v2">'
    if footer_marker in html:
        html = html.replace(footer_marker, bloque_vecinos + "\n\n        " + footer_marker, 1)
    else:
        print(f"⚠️  {slug}: no se encontró <footer class='footer-v2'>, buscando </body>")
        if "</body>" in html:
            html = html.replace("</body>", bloque_vecinos + "\n\n    </body>", 1)
        else:
            print(f"❌ {slug}: no se encontró ningún marcador de footer")
            return None
    
    # --- 2. Insertar bloque de blog tras el primer <h2> ---
    # Buscar el primer <h2> que no sea del bloque recién insertado
    idx_h2 = html.find("<h2>")
    if idx_h2 >= 0:
        # Buscar el cierre </h2> de ese tag
        idx_close = html.find("</h2>", idx_h2)
        if idx_close >= 0:
            insert_point = idx_close + len("</h2>")
            html = html[:insert_point] + "\n" + bloque_blog + html[insert_point:]
    
    return html


def procesar_lote(inicio, fin):
    """
    Procesa un lote de slugs (de inicio a fin en la lista ordenada).
    Retorna (procesados, errores)
    """
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
        print(f"✅ {slug}")
    
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
    
    print(f"\n📊 RESUMEN:")
    print(f"   Procesados: {total}")
    print(f"   Errores: {len(errores)}")
    for e in errores:
        print(f"   ⚠️  {e}")
    
    if total > 0:
        print(f"   ✅ Lote completado")
    else:
        print(f"   ❌ Sin páginas procesadas")
