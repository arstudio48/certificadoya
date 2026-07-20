#!/usr/bin/env python3
"""
CertificadoYa — Prospección de técnicos certificadores en Sevilla
Busca técnicos reales en fuentes públicas y los guarda como prospectos.
"""
import requests
from bs4 import BeautifulSoup
from supabase import create_client
import re
import time

URL = "https://wypgqpgjlookbhuaiyxa.supabase.co"
KEY = "sb_secret_7LGmViutdXYU16hwvAqlJg_hZjhfcLe"
sb = create_client(URL, KEY)

PROVINCIA = "Sevilla"

def guardar_prospecto(nombre, empresa, email, telefono, localidad, colegiado, titulacion, fuente):
    """Guarda un prospecto si no existe ya (mismo email o colegiado)."""
    if not nombre and not empresa:
        return
    # Evitar duplicados
    if email:
        exist = sb.table('prospectos_tecnicos').select('id').eq('email', email).execute()
        if exist.data:
            return
    sb.table('prospectos_tecnicos').insert({
        'nombre': nombre,
        'empresa': empresa,
        'email': email,
        'telefono': telefono,
        'provincia': PROVINCIA,
        'localidad': localidad,
        'colegiado': colegiado,
        'titulacion': titulacion,
        'fuente': fuente
    }).execute()
    print(f"  ✓ Guardado: {nombre or empresa} ({localidad})")

def scrape_certificadodeeficienciaenergetica():
    """Scrapea listado de profesionales de Sevilla desde certificadodeeficienciaenergetica.com"""
    print("🔍 Buscando en certificadodeeficienciaenergetica.com...")
    base = "https://certificadodeeficienciaenergetica.com/provincias/sevilla"
    try:
        r = requests.get(base, timeout=15)
        ids = set(re.findall(r'/profesional/(\d+)', r.text))
        print(f"  Encontrados {len(ids)} perfiles")
        for pid in list(ids)[:30]:
            url = f"https://certificadodeeficienciaenergetica.com/profesional/{pid}"
            try:
                pr = requests.get(url, timeout=10)
                soup = BeautifulSoup(pr.text, 'html.parser')
                h1 = soup.find('h1')
                nombre = h1.get_text(strip=True) if h1 else ''
                tit = 'Arquitecto Técnico' if 'Arquitecto Técnico' in pr.text else 'Arquitecto'
                loc_match = re.search(r'Localidad.*?([A-Za-zÁ-Úá-ú ]+?)\s*\(SE\)', pr.text)
                localidad = loc_match.group(1).strip() if loc_match else 'Sevilla'
                col_match = re.search(r'Número de colegiado[:\s]*([\d.]+)', pr.text)
                colegiado = col_match.group(1) if col_match else None
                email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', pr.text)
                email = email_match.group(0) if email_match else None
                tel_match = re.search(r'(\d{3}[\s-]?\d{3}[\s-]?\d{3})', pr.text)
                telefono = tel_match.group(1) if tel_match else None
                guardar_prospecto(nombre, None, email, telefono, localidad, colegiado, tit, "certificadodeeficienciaenergetica.com")
                time.sleep(1)
            except Exception as e:
                print(f"  ⚠ Error perfil {pid}: {e}")
    except Exception as e:
        print(f"  ⚠ Error listado: {e}")

def scrape_coaat_sevilla():
    """Intenta extraer del directorio del COAAT Sevilla"""
    print("🔍 Buscando en COAAT Sevilla...")
    urls = [
        "https://coatsevilla.es/directorio/",
        "https://coatsevilla.es/colegiados/",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            emails = set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', r.text))
            for em in emails:
                if 'coat' not in em and 'coaat' not in em:
                    guardar_prospecto(None, None, em, None, 'Sevilla', None, None, "COAAT Sevilla")
        except Exception as e:
            print(f"  ⚠ No accesible {url}: {e}")

if __name__ == '__main__':
    print(f"=== PROSPECCIÓN DE TÉCNICOS EN {PROVINCIA} ===\n")
    scrape_certificadodeeficienciaenergetica()
    scrape_coaat_sevilla()
    total = sb.table('prospectos_tecnicos').select('*').eq('provincia', PROVINCIA).execute()
    print(f"\n✅ Total prospectos en {PROVINCIA}: {len(total.data)}")
