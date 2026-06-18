#!/bin/bash
cd /home/arturo/certificadoya
echo "=== precio-madrid ==="
grep -c 'enlaces-blog' precio-certificado-energetico-madrid/index.html || echo 0
grep -c 'provincias-cercanas' precio-certificado-energetico-madrid/index.html || echo 0
grep -c 'registro-ccaa' precio-certificado-energetico-madrid/index.html || echo 0

echo "=== INVENTARIO cercanas ==="
for f in certificado-energetico-*/index.html; do
  n=$(grep -o 'href="/certificado-energetico-[a-z-]*/"' "$f" | grep -c .)
  echo "$f $n"
done | sort -k2 -n | head -40
