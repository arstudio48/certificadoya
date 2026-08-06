#!/bin/bash
# =============================================================================
# CertificadoYa — Iniciar servicio de modelo local
# =============================================================================
# Script simplificado para arrancar el proxy y verificar que responde.
# Uso: ./iniciar-modelo-local.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER="$SCRIPT_DIR/servir-modelo-local.sh"
PORT=8118

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CertificadoYa — Iniciar Modelo Local"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Arrancar el proxy en background
echo ""
echo "▶ Arrancando proxy en puerto $PORT …"
bash "$LAUNCHER" --daemon

# 2. Verificar que responde
echo ""
echo "▶ Verificando health endpoint…"
sleep 2
if curl -sf "http://localhost:$PORT/health" > /dev/null 2>&1; then
    echo "✓ Proxy responde correctamente en http://localhost:$PORT"
    echo ""
    echo "  Endpoints disponibles:"
    echo "    GET  /health              → estado del servicio"
    echo "    POST /generate            → generar texto (modelo + prompt)"
    echo "    POST /chat                → chat multi-turno (modelo + messages)"
    echo "    POST /generar-presupuesto → generar presupuesto CEE"
    echo "    POST /responder-faq       → responder FAQ sobre CEE"
    echo ""
    echo "  Log: /home/arturo/certificadoya/.hermes/modelo-local.log"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "✗ ERROR: El proxy no responde en :$PORT"
    echo "  Revisa el log: /home/arturo/certificadoya/.hermes/modelo-local.log"
    exit 1
fi
