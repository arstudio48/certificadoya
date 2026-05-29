#!/bin/bash
# =============================================================================
# CertificadoYa — Servicio de modelos locales (launcher bash)
# =============================================================================
# Verifica Ollama, arranca el proxy Python y mantiene el servicio.
# Uso:
#   ./servir-modelo-local.sh            # foreground
#   ./servir-modelo-local.sh --daemon   # background (nohup)
#   ./servir-modelo-local.sh --stop     # mata el proceso
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/servir-modelo-local.py"
PYTHON_BIN="/usr/bin/python3.12"
PIDFILE="/tmp/certificadoya-modelo-local.pid"
LOGDIR="/home/arturo/certificadoya/.hermes"
LOG="$LOGDIR/modelo-local.log"
PORT=8118

mkdir -p "$LOGDIR"

# ── helpers ────────────────────────────────────────────────────────────────

log()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
err()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG" >&2; }

usage() {
    cat <<EOF
Uso: $(basename "$0") [--daemon | --stop | --status]

Opciones:
  --daemon   Arrancar en background (nohup)
  --stop     Detener el proceso en background
  --status   Ver estado del proceso
  (sin args) Arrancar en foreground
EOF
    exit 0
}

check_deps() {
    command -v "$PYTHON_BIN" >/dev/null 2>&1 || { err "$PYTHON_BIN no encontrado"; exit 1; }
    command -v curl    >/dev/null 2>&1 || { err "curl no encontrado";    exit 1; }
}

check_ollama() {
    if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
        log "✓ Ollama está corriendo en localhost:11434"
        return 0
    fi
    log "⚠ Ollama no responde. Intentando arrancar…"
    if command -v ollama >/dev/null 2>&1; then
        nohup ollama serve >/dev/null 2>&1 &
        # Esperar hasta 15s
        for i in $(seq 1 30); do
            sleep 0.5
            if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
                log "✓ Ollama arrancado correctamente"
                return 0
            fi
        done
        err "No se pudo arrancar Ollama tras 15s"
        return 1
    else
        err "Comando 'ollama' no encontrado en PATH"
        return 1
    fi
}

wait_for_ready() {
    log "Esperando a que el proxy responda en :$PORT/health …"
    for i in $(seq 1 20); do
        sleep 0.5
        if curl -sf "http://localhost:$PORT/health" >/dev/null 2>&1; then
            log "✓ Proxy listo en http://localhost:$PORT"
            curl -s "http://localhost:$PORT/health" | "$PYTHON_BIN" -m json.tool 2>/dev/null | head -10
            return 0
        fi
    done
    err "El proxy no respondió tras 10s — revisa $LOG"
    return 1
}

# ── acciones ───────────────────────────────────────────────────────────────

do_start_foreground() {
    check_deps
    check_ollama || exit 1
    log "Arrancando proxy en foreground (puerto $PORT)…"
    exec "$PYTHON_BIN" "$PYTHON_SCRIPT"
}

do_start_daemon() {
    check_deps
    check_ollama || exit 1

    if [ -f "$PIDFILE" ]; then
        OLD_PID=$(cat "$PIDFILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            err "Ya hay un proceso corriendo (PID $OLD_PID). Usa --stop primero."
            exit 1
        fi
        rm -f "$PIDFILE"
    fi

    log "Arrancando proxy en background (puerto $PORT)…"
    nohup "$PYTHON_BIN" "$PYTHON_SCRIPT" >> "$LOG" 2>&1 &
    BGPID=$!
    echo "$BGPID" > "$PIDFILE"
    log "PID $BGPID — esperando confirmación…"

    if wait_for_ready; then
        log "✓ Servicio iniciado (PID $BGPID)"
    else
        err "Fallo al iniciar el servicio"
        kill "$BGPID" 2>/dev/null || true
        rm -f "$PIDFILE"
        exit 1
    fi
}

do_stop() {
    if [ ! -f "$PIDFILE" ]; then
        # Buscar por nombre
        PIDS=$(pgrep -f "servir-modelo-local.py" 2>/dev/null || true)
        if [ -n "$PIDS" ]; then
            log "Deteniendo procesos: $PIDS"
            kill $PIDS 2>/dev/null || true
            sleep 1
            log "✓ Procesos detenidos"
        else
            err "No hay proceso activo de servir-modelo-local"
        fi
        return 0
    fi

    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
        log "Deteniendo PID $PID …"
        kill "$PID" 2>/dev/null || true
        sleep 1
        if kill -0 "$PID" 2>/dev/null; then
            kill -9 "$PID" 2>/dev/null || true
        fi
        log "✓ Detenido"
    else
        err "PID $PID no existe (ya terminó)"
    fi
    rm -f "$PIDFILE"
}

do_status() {
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Estado: ACTIVO (PID $PID)"
            echo "Endpoint: http://localhost:$PORT/health"
            curl -sf "http://localhost:$PORT/health" 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "(no responde aún)"
        else
            echo "Estado: PID file existe pero proceso muerto"
            rm -f "$PIDFILE"
        fi
    else
        # Buscar por nombre
        PIDS=$(pgrep -f "servir-modelo-local.py" 2>/dev/null || true)
        if [ -n "$PIDS" ]; then
            echo "Estado: ACTIVO (PID $PIDS) — sin PID file"
            echo "Endpoint: http://localhost:$PORT/health"
            curl -sf "http://localhost:$PORT/health" 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "(no responde aún)"
        else
            echo "Estado: INACTIVO"
        fi
    fi
}

# ── main ───────────────────────────────────────────────────────────────────

case "${1:-}" in
    --daemon|--start|-d)  do_start_daemon    ;;
    --stop|-k)            do_stop            ;;
    --status|-s)          do_status          ;;
    --help|-h)            usage              ;;
    *)                    do_start_foreground ;;
esac
