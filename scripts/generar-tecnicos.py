#!/usr/bin/env python3
"""Generador de perfiles publicos de tecnicos para CertificadoYa.es"""
import json, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE, "data", "tecnicos.json")
OUTPUT_DIR = os.path.join(BASE, "tecnicos")

def slugify(nombre):
    nombre = nombre.lower().strip()
    nombre = re.sub(r'[áàäâ]', 'a', nombre)
    nombre = re.sub(r'[éèëê]', 'e', nombre)
    nombre = re.sub(r'[íìïî]', 'i', nombre)
    nombre = re.sub(r'[óòöô]', 'o', nombre)
    nombre = re.sub(r'[úùüû]', 'u', nombre)
    nombre = re.sub(r'[ñ]', 'n', nombre)
    nombre = re.sub(r'[^a-z0-9\s-]', '', nombre)
    nombre = re.sub(r'\s+', '-', nombre.strip())
    return re.sub(r'-+', '-', nombre)

def generar_pagina_tecnico(t):
    slug = slugify(t["nombre"])
    dir_path = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(dir_path, exist_ok=True)
    
    nombre = t["nombre"]
    profesion = t["profesion"]
    ciudad = t["ciudad"]
    provincia = t["provincia"]
    web = t.get("web", "")
    especialidad = t.get("especialidad", "Certificacion energetica general")
    experiencia = t.get("experiencia", 0)
    disponible = t.get("disponible", True)
    
    disp = '<span style="color:#547c24;font-weight:600">Disponible</span>' if disponible else '<span style="color:#999">No disponible temporalmente</span>'
    prov_link = f"/certificado-energetico-{provincia}/"
    
    # Build web button only if URL exists
    web_btn = f'<a href="{web}" class="btn-web" target="_blank" rel="nofollow noopener">Visitar su web</a>' if web else ''
    
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{nombre} - {profesion} Certificado Energetico {ciudad} | CertificadoYa</title>
  <meta name="description" content="{nombre}, {profesion} especializado en certificacion energetica en {ciudad}. {experiencia} anos de experiencia. Solicita presupuesto sin compromiso.">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23547c24'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-family='sans-serif'>C</text></svg>">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.min.css">
  <style>
    *{{font-family:Outfit,sans-serif;margin:0;padding:0;box-sizing:border-box}}
    body{{background:#f5f7f2;color:#1a1a1a;line-height:1.6}}
    .perfil-container{{max-width:900px;margin:0 auto;padding:2rem 1rem}}
    .perfil-card{{background:#fff;border-radius:16px;padding:2.5rem;box-shadow:0 2px 12px rgba(0,0,0,.06);margin-bottom:1.5rem}}
    .perfil-header{{display:flex;align-items:center;gap:1.5rem;margin-bottom:2rem;flex-wrap:wrap}}
    .avatar{{width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#547c24,#7aa844);display:flex;align-items:center;justify-content:center;font-size:2rem;color:#fff;font-weight:700;flex-shrink:0}}
    .perfil-title h1{{font-size:1.5rem;font-weight:600;margin-bottom:.2rem}}
    .perfil-title .profesion{{color:#547c24;font-weight:500;font-size:.95rem}}
    .perfil-meta{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-bottom:1.5rem}}
    .meta-item{{padding:.8rem;background:#f8faf5;border-radius:10px}}
    .meta-label{{font-size:.75rem;color:#9aab8a;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.2rem}}
    .meta-value{{font-size:.95rem;font-weight:500;color:#1a1a1a}}
    .btn-contacto{{display:inline-block;padding:.8rem 2rem;background:#547c24;color:#fff;border-radius:8px;font-weight:600;text-decoration:none;transition:background .2s;margin-top:.5rem}}
    .btn-contacto:hover{{background:#3d5e1a}}
    .btn-web{{display:inline-block;padding:.8rem 2rem;background:transparent;color:#547c24;border:2px solid #547c24;border-radius:8px;font-weight:600;text-decoration:none;transition:all .2s;margin-top:.5rem;margin-left:.5rem}}
    .btn-web:hover{{background:#f0f5ea}}
    .breadcrumb{{font-size:.82rem;color:#9aab8a;margin-bottom:1.5rem}}
    .breadcrumb a{{color:#547c24;text-decoration:none}}
    .breadcrumb a:hover{{text-decoration:underline}}
    @media(max-width:480px){{.perfil-card{{padding:1.5rem}}.perfil-header{{flex-direction:column;text-align:center}}.btn-web{{margin-left:0;margin-top:.5rem;display:block;text-align:center}}.btn-contacto{{display:block;text-align:center}}}}
  </style>
</head>
<body>
  <div class="perfil-container">
    <div class="breadcrumb">
      <a href="/">Inicio</a> &gt; <a href="/tecnicos/">Tecnicos</a> &gt; {nombre}
    </div>
    <div class="perfil-card">
      <div class="perfil-header">
        <div class="avatar">{nombre[0]}</div>
        <div class="perfil-title">
          <h1>{nombre}</h1>
          <div class="profesion">{profesion}</div>
          <div style="margin-top:.3rem;font-size:.85rem;color:#666">{disp}</div>
        </div>
      </div>
      <div class="perfil-meta">
        <div class="meta-item">
          <div class="meta-label">Ubicacion</div>
          <div class="meta-value">{ciudad}</div>
        </div>
        <div class="meta-item">
          <div class="meta-label">Provincia</div>
          <div class="meta-value"><a href="{prov_link}" style="color:#547c24;text-decoration:none">{provincia.title()}</a></div>
        </div>
        <div class="meta-item">
          <div class="meta-label">Experiencia</div>
          <div class="meta-value">{experiencia} anos</div>
        </div>
        <div class="meta-item">
          <div class="meta-label">Especialidad</div>
          <div class="meta-value">{especialidad}</div>
        </div>
      </div>
      <p style="color:#555;margin-bottom:1.2rem;font-size:.92rem">{nombre} es {profesion.lower()} colegiado con {experiencia} anos de experiencia en certificacion energetica en {ciudad} y toda la provincia. Especializado en {especialidad.lower()}.</p>
      <div style="display:flex;flex-wrap:wrap;gap:.5rem">
        <a href="/#presupuesto" class="btn-contacto">Solicitar presupuesto</a>
        {web_btn}
      </div>
    </div>
    <div class="perfil-card" style="background:#f0f5ea;text-align:center">
      <h3 style="font-size:1rem;margin-bottom:.5rem">? Necesitas un certificado energetico en {ciudad}?</h3>
      <p style="font-size:.88rem;color:#555;margin-bottom:.8rem">Presupuesto instantaneo por m2. Te asignamos el tecnico mas cercano.</p>
      <a href="/#presupuesto" style="color:#547c24;font-weight:600;text-decoration:none">Calcular presupuesto</a>
    </div>
  </div>
</body>
</html>'''
    
    filepath = os.path.join(dir_path, "index.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    return slug, filepath

def generar_indice_tecnicos(tecnicos_list):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    cards_html = ""
    for t in tecnicos_list:
        slug = slugify(t["nombre"])
        nombre = t["nombre"]
        profesion = t["profesion"]
        ciudad = t["ciudad"]
        disponible = t.get("disponible", True)
        badge = '<span style="font-size:.7rem;color:#547c24;font-weight:500">Disponible</span>' if disponible else '<span style="font-size:.7rem;color:#999">No disponible</span>'
        
        cards_html += f'''
        <a href="/tecnicos/{slug}/" style="text-decoration:none;color:inherit;display:block">
          <div style="background:#fff;border-radius:12px;padding:1.2rem;box-shadow:0 1px 6px rgba(0,0,0,.05);transition:transform .15s;border:1px solid #e8ede2">
            <div style="display:flex;align-items:center;gap:.8rem;margin-bottom:.6rem">
              <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#547c24,#7aa844);display:flex;align-items:center;justify-content:center;font-size:1.1rem;color:#fff;font-weight:700;flex-shrink:0">{nombre[0]}</div>
              <div>
                <div style="font-weight:600;font-size:.92rem">{nombre}</div>
                <div style="font-size:.8rem;color:#547c24">{profesion}</div>
              </div>
            </div>
            <div style="font-size:.82rem;color:#666;display:flex;justify-content:space-between;align-items:center">
              <span>{ciudad}</span>
              {badge}
            </div>
          </div>
        </a>'''
    
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tecnicos Certificadores CertificadoYa - Expertos en CEE en toda Espana</title>
  <meta name="description" content="Directorio de tecnicos certificadores de eficiencia energetica en Espana. Arquitectos, ingenieros y arquitectos tecnicos verificados en todas las provincias.">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23547c24'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-family='sans-serif'>C</text></svg>">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.min.css">
  <style>
    *{{font-family:Outfit,sans-serif;margin:0;padding:0;box-sizing:border-box}}
    body{{background:#f5f7f2;color:#1a1a1a}}
    .container{{max-width:1000px;margin:0 auto;padding:2rem 1rem}}
    h1{{font-size:1.8rem;margin-bottom:.3rem}}
    .subtitle{{color:#666;font-size:.95rem;margin-bottom:2rem}}
    .grid-tecnicos{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem}}
    .breadcrumb{{font-size:.82rem;color:#9aab8a;margin-bottom:1.5rem}}
    .breadcrumb a{{color:#547c24;text-decoration:none}}
    .contador{{font-size:.9rem;color:#547c24;font-weight:600;margin-bottom:1.5rem}}
    .cta-final{{background:#fff;border-radius:16px;padding:2rem;text-align:center;margin-top:2rem;box-shadow:0 2px 12px rgba(0,0,0,.06)}}
    .cta-final h3{{font-size:1.1rem;margin-bottom:.5rem}}
    .cta-btn{{display:inline-block;padding:.7rem 1.8rem;background:#547c24;color:#fff;border-radius:8px;font-weight:600;text-decoration:none;margin-top:.8rem;transition:background .2s}}
    .cta-btn:hover{{background:#3d5e1a}}
    @media(max-width:480px){{h1{{font-size:1.4rem}}.grid-tecnicos{{grid-template-columns:1fr}}}}
  </style>
</head>
<body>
  <div class="container">
    <div class="breadcrumb">
      <a href="/">Inicio</a> &gt; Tecnicos
    </div>
    <h1>Tecnicos Certificadores</h1>
    <p class="subtitle">Todos nuestros tecnicos son profesionales colegiados verificados. Encuentra el mas cercano a tu zona.</p>
    <div class="contador">{len(tecnicos_list)} tecnicos disponibles en toda Espana</div>
    <div class="grid-tecnicos">
      {cards_html}
    </div>
    <div class="cta-final">
      <h3>Eres tecnico certificador?</h3>
      <p style="font-size:.88rem;color:#555">Unete a CertificadoYa y recibe leads de clientes en tu zona. Sin compromisos, eliges cuando aceptar trabajos.</p>
      <a href="/panel-tecnicos.html" class="cta-btn">Registrarme como tecnico</a>
    </div>
  </div>
</body>
</html>'''
    
    filepath = os.path.join(OUTPUT_DIR, "index.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    return filepath

if __name__ == "__main__":
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    tecnicos = data["tecnicos"]
    generados = []
    
    for t in tecnicos:
        slug, path = generar_pagina_tecnico(t)
        generados.append((t["nombre"], slug, path))
        print(f"OK {t['nombre']} -> /tecnicos/{slug}/")
    
    generar_indice_tecnicos(tecnicos)
    print(f"\nIndice de tecnicos generado: /tecnicos/")
    print(f"\nTotal: {len(generados)} perfiles creados")
