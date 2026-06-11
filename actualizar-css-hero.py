#!/usr/bin/env python3
"""Actualiza el CSS hero-split en todas las landing pages"""
import os

OLD = """.hero-split { display:flex; gap:2rem; align-items:center; max-width:900px; margin:0 auto 3rem; }
  .hero-split .hero-img { flex:0 0 280px; border-radius:var(--radius); overflow:hidden; box-shadow:var(--shadow); }
  .hero-split .hero-img img { width:100%; height:auto; display:block; }
  .hero-split .presupuesto-card { flex:1; max-width:100%; margin:0; }
  @media (max-width:700px) { .hero-split { flex-direction:column; } .hero-split .hero-img { flex:0 0 auto; max-width:200px; } }"""

NEW = """.hero-split { display:flex; gap:2rem; align-items:center; max-width:1000px; margin:0 auto 2rem; }
  .hero-split .hero-img { flex:0 0 320px; border-radius:var(--radius); overflow:hidden; box-shadow:var(--shadow); }
  .hero-split .hero-img img { width:100%; height:auto; display:block; }
  .hero-split .presupuesto-card { flex:1; max-width:100%; margin:0; }
  @media (max-width:700px) { .hero-split { flex-direction:column; } .hero-split .hero-img { flex:0 0 auto; max-width:220px; } }"""

# Usar 2 espacios de indent como el original
OLD = OLD.replace("  ", "  ")
NEW = NEW.replace("  ", "  ")

base = "/home/arturo/certificadoya"
for entry in os.listdir(base):
    if entry.startswith("certificado-energetico-"):
        path = os.path.join(base, entry, "index.html")
        if os.path.exists(path):
            with open(path) as f:
                html = f.read()
            if OLD in html:
                count = html.count(OLD)
                html = html.replace(OLD, NEW)
                with open(path, 'w') as f:
                    f.write(html)
                print("  OK {} ({} reemplazos)".format(entry, count))
            else:
                print("  -- {} (no encontrado)".format(entry))
