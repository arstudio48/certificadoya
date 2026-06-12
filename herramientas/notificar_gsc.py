# -*- coding: utf-8 -*-
"""Envía el sitemap a Google Search Console usando ADC (artbriher@gmail.com)."""
import sys
import os
import requests
from google.auth import default
from google.auth.transport.requests import Request

URL_SITEMAP = "https://www.certificadoya.es/sitemap.xml"
PROPIEDADES = ["sc-domain:certificadoya.es",
               "https://www.certificadoya.es/"]
AMBITO = ["https://www.googleapis.com/auth/webmasters"]
QUOTA_PROJECT = "certificadoya-seo"


def obtener_token():
    os.environ["GOOGLE_CLOUD_QUOTA_PROJECT"] = QUOTA_PROJECT
    credenciales, _ = default(scopes=AMBITO)
    if not credenciales.valid:
        credenciales.refresh(Request())
    return credenciales.token


def enviar_sitemap():
    token = obtener_token()
    cabeceras = {"Authorization": f"Bearer {token}",
                 "X-Goog-User-Project": QUOTA_PROJECT}
    for propiedad in PROPIEDADES:
        prop_cod = requests.utils.quote(propiedad, safe="")
        mapa_cod = requests.utils.quote(URL_SITEMAP, safe="")
        url = (f"https://www.googleapis.com/webmasters/v3/sites/"
               f"{prop_cod}/sitemaps/{mapa_cod}")
        respuesta = requests.put(url, headers=cabeceras, timeout=30)
        if respuesta.status_code in (200, 204):
            print(f"GSC OK — sitemap enviado a {propiedad} "
                  f"(HTTP {respuesta.status_code})")
            return 0
        print(f"GSC aviso — {propiedad}: HTTP {respuesta.status_code} "
              f"{respuesta.text[:200]}")
    print("GSC ERROR — ninguna propiedad aceptó el envío.")
    return 1


if __name__ == "__main__":
    sys.exit(enviar_sitemap())
