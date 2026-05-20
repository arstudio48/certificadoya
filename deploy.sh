#!/bin/bash
# Deploy script for CertificaYA
# Usage: ./deploy.sh
# Requires: VERCEL_TOKEN env var or pass as argument
set -e

TOKEN="${1:-$VERCEL_TOKEN}"
if [ -z "$TOKEN" ]; then
  echo "Usage: deploy.sh <vercel_token>"
  exit 1
fi

cd /opt/data/projects/certificadoya

echo "🏗️  Building..."
npx vercel pull --yes --token "$TOKEN" 2>&1 | tail -1
npx vercel build --prod --token "$TOKEN" 2>&1 | tail -1

echo "🧹 Removing extensionless files (they shadow .html)..."
rm -f .vercel/output/static/index .vercel/output/static/panel-tecnicos 2>/dev/null
rm -f .vercel/output/static/legal/aviso-legal .vercel/output/static/legal/privacidad .vercel/output/static/legal/cookies 2>/dev/null

echo "🚀 Deploying..."
npx vercel deploy --prebuilt --prod --yes --token "$TOKEN" 2>&1 | tail -5

echo ""
echo "✅ Verifying..."
sleep 3
curl -sL "https://www.certificadoya.es/" | grep -q 'nav-toggle' && echo "✅ HTML deployed OK" || echo "❌ HTML check failed!"
curl -sL "https://www.certificadoya.es/css/style.css" | grep -q 'max-width: 480px' && echo "✅ CSS responsive OK" || echo "❌ CSS check failed!"
curl -sL "https://www.certificadoya.es/panel-tecnicos.html" | grep -q 'Únete como técnico' && echo "✅ Panel técnicos OK" || echo "❌ Panel check failed!"
echo "🏁 Done"
