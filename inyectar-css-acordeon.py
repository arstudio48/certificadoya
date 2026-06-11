#!/usr/bin/env python3
"""Inyecta CSS de acordeón en landings que no lo tengan"""
import os, re

BASE = "/home/arturo/certificadoya"
CSS = """
  .accordion-section { margin-bottom:.75rem; border:1px solid var(--gray-200); border-radius:var(--radius); overflow:hidden; background:var(--white); }
  .accordion-section summary { display:flex; align-items:center; gap:.5rem; padding:1rem 1.25rem; font-weight:600; font-size:1rem; cursor:pointer; color:var(--gray-800); background:var(--gray-50); user-select:none; list-style:none; transition:background .15s; }
  .accordion-section summary::-webkit-details-marker { display:none; }
  .accordion-section summary::after { content:'▾'; margin-left:auto; font-size:.85rem; color:var(--green); transition:transform .2s; }
  .accordion-section[open] summary { background:var(--green-light); }
  .tabla-precios { width:100%; border-collapse:collapse; margin:1.5rem 0; border-radius:8px; overflow:hidden; box-shadow:var(--shadow); }
  .tabla-precios th { background:var(--green); color:white; padding:.75rem 1rem; text-align:left; font-weight:600; font-size:.9rem; }
  .tabla-precios td { padding:.65rem 1rem; border-bottom:1px solid var(--gray-200); font-size:.9rem; }
  .tabla-precios tr:nth-child(even) { background:var(--gray-50); }
  .tabla-precios tr:hover { background:var(--green-light); }
"""

modified = 0
for entry in sorted(os.listdir(BASE)):
    if not entry.startswith("certificado-energetico-"):
        continue
    fpath = os.path.join(BASE, entry, "index.html")
    if not os.path.exists(fpath):
        continue
    
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Skip if already has accordion CSS
    if "accordion-section {" in html:
        print(f"  ⏭️  {entry} — ya tiene CSS acordeón")
        continue
    
    # Skip if no accordion HTML
    if 'accordion-section"' not in html:
        print(f"  ⏭️  {entry} — no tiene acordeón HTML")
        continue
    
    # Inject CSS before </style>
    html = html.replace("</style>", CSS + "\n</style>", 1)
    
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)
    modified += 1
    # Fix the CSS for madrid - it already had a tab-precios closer
    print(f"  ✅ {entry} — CSS acordeón añadido")

print(f"\nTotal: {modified} landings actualizadas con CSS acordeón")
