#!/usr/bin/env python3
"""Personaliza cada landing page: color único + posición de imagen alternada"""

import os

CIUDADES = [
    ("a-coruna", "A Coruña", "#1E6F9F", "left"),
    ("alicante", "Alicante", "#E8590C", "right"),
    ("cordoba", "Córdoba", "#2B9348", "left"),
    ("gijon", "Gijón", "#00509D", "right"),
    ("granada", "Granada", "#9B2226", "left"),
    ("malaga", "Málaga", "#0077B6", "right"),
    ("palma", "Palma", "#0B525B", "left"),
    ("salamanca", "Salamanca", "#936639", "right"),
    ("santiago", "Santiago", "#2D6A4F", "left"),
    ("segovia", "Segovia", "#BC3908", "right"),
    ("toledo", "Toledo", "#A68A56", "left"),
]

def personalizar(slug, nombre, color, lado):
    ruta = "/home/arturo/certificadoya/certificado-energetico-{}/index.html".format(slug)
    if not os.path.exists(ruta):
        print("  XXX {}: no existe".format(nombre))
        return False

    with open(ruta) as f:
        html = f.read()
    original = html

    # 1. Clase ciudad en hero-split
    html = html.replace('<div class="hero-split">', '<div class="hero-split ciudad-{}">'.format(slug))

    # 2. CSS específico de la ciudad
    css_lines = []
    css_lines.append(".ciudad-{} {{ --accent: {}; }}".format(slug, color))
    css_lines.append(".ciudad-{} .hero-img {{ border-color: {}; border: 3px solid {}; }}".format(slug, color, color))
    css_lines.append(".ciudad-{} .presupuesto-card {{ border-top: 4px solid {}; }}".format(slug, color))
    if lado == "right":
        css_lines.append(".ciudad-{} {{ flex-direction: row-reverse; }}".format(slug))
    
    css_bloque = "\n    " + "\n    ".join(css_lines) + "\n"
    html = html.replace("</style>", css_bloque + "</style>", 1)

    if html != original:
        with open(ruta, 'w') as f:
            f.write(html)
        print("  OK {}: color {}, imagen a la {}".format(nombre, color, lado))
        return True
    else:
        print("  -- {}: sin cambios".format(nombre))
        return False

if __name__ == '__main__':
    print("Personalizando ciudades...\n")
    for slug, nombre, color, lado in CIUDADES:
        personalizar(slug, nombre, color, lado)
    print("\nHecho")
