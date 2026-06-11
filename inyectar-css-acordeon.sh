#!/bin/bash
# Inyecta CSS de acordeón en todas las landings que no lo tengan
CSSBODY="
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
"

for DIR in /home/arturo/certificadoya/certificado-energetico-*/; do
  FILE="${DIR}index.html"
  [ -f "$FILE" ] || continue
  
  # Skip if already has accordion CSS
  if grep -q 'accordion-section {' "$FILE"; then
    echo "  ⏭️  $(basename $DIR) — ya tiene CSS acordeón"
    continue
  fi
  
  # Check if it has accordion HTML (from the content replacement)
  if ! grep -q 'accordion-section"' "$FILE"; then
    echo "  ⏭️  $(basename $DIR) — no tiene acordeón HTML"
    continue
  fi
  
  # Insert CSS before </style>
  sed -i '/<\/style>/i'"$CSSBODY" "$FILE"
  echo "  ✅ $(basename $DIR) — CSS acordeón añadido"
done

echo "--- Hecho ---"
