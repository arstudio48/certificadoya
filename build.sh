#!/bin/bash
# Vercel build script: copia HTMLs sin extensión para evitar el problema de cleanUrls
set -e

echo "📦 Build: generando archivos sin extensión..."

# Copiar tecnicos/index.html → tecnicos (sin extensión)
cp tecnicos/index.html tecnicos
echo "  ✅ /tecnicos"

# Copiar legal/*.html → legal/* (sin extensión)
for f in legal/*.html; do
  base=$(basename "$f" .html)
  cp "$f" "legal/$base"
  echo "  ✅ /legal/$base"
done

echo "🏁 Build completado"
