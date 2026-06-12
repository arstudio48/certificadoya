#!/usr/bin/env bash
# Despliegue completo: sube cambios a GitHub, notifica IndexNow y GSC.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== DESPLIEGUE: push a GitHub ==="
git push

echo ""
echo "=== NOTIFICAR IndexNow ==="
python3 herramientas/notificar_indexnow.py && echo "IndexNow OK" || echo "IndexNow ERROR (no crítico)"

echo ""
echo "=== NOTIFICAR Google Search Console ==="
python3 herramientas/notificar_gsc.py && echo "GSC OK" || echo "GSC ERROR (no crítico)"

echo ""
echo "=== DESPLIEGUE COMPLETO ==="
