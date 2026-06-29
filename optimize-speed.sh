#!/bin/bash
# Script de optimización de velocidad para certificadoya.es
# Ejecutar: bash optimize-speed.sh

echo "🚀 Optimizando velocidad de certificadoya.es..."

# 1. Minificar CSS (eliminar espacios, comentarios)
echo "📦 Minificando CSS..."
npx clean-css-cli style.css -o style.min.css --compatibility ie8

# 2. Minificar HTML (eliminar espacios en blanco)
echo "📦 Minificando HTML..."
# Instalar html-minifier si no existe
npm install -g html-minifier 2>/dev/null || true

# Minificar index.html principal
npx html-minifier \
  --collapse-whitespace \
  --remove-comments \
  --remove-optional-tags \
  --remove-redundant-attributes \
  --remove-script-type-attributes \
  --remove-tag-whitespace \
  --use-short-doctype \
  --minify-css true \
  --minify-js true \
  index.html -o index.min.html

echo "✅ Optimización completada!"
echo ""
echo "Archivos generados:"
echo "  - style.min.css (CSS minificado)"
echo "  - index.min.html (HTML minificado)"
echo ""
echo "Comparación de tamaños:"
ls -lh style.css style.min.css 2>/dev/null || echo "CSS minificado no generado"
ls -lh index.html index.min.html 2>/dev/null || echo "HTML minificado no generado"
