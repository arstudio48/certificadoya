#!/usr/bin/python3.12
"""
CertificadoYa — Servicio de modelos locales via Ollama
API HTTP en puerto 8118 que expone modelos locales a la app web.
"""

import json
import logging
import os
import subprocess
import sys
import time
import threading
from datetime import datetime, timezone
from http import HTTPStatus

import requests
from flask import Flask, jsonify, request

# ── Configuración ──────────────────────────────────────────────────────────

LOG_DIR = os.path.expanduser("/home/arturo/certificadoya/.hermes")
LOG_FILE = os.path.join(LOG_DIR, "modelo-local.log")
HOST = "0.0.0.0"
PORT = 8118
OLLAMA_BASE = "http://localhost:11434"
OLLAMA_TIMEOUT = 60         # segundos
DEFAULT_MODEL = "qwen2.5:7b-instruct-q4_K_M"

GPU_LABEL = "RTX 4060 8GB"
AVAILABLE_MODELS = [
    "qwen2.5-coder:7b-instruct-q4_K_M",
    "qwen2.5:7b-instruct-q4_K_M",
    "gemma3:4b",
    "phi4-mini:3.8b-q4_K_M",
    "llama3.1:8b",
    "llama3.2:3b",
]

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("modelo-local")

app = Flask(__name__)

# ── Timestamp de arranque ──────────────────────────────────────────────────

_start_time = datetime.now(timezone.utc)


# ── CORS (manual, para Flask sin extensiones) ─────────────────────────────

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ── Helpers ────────────────────────────────────────────────────────────────

def _uptime():
    delta = datetime.now(timezone.utc) - _start_time
    total_seconds = int(delta.total_seconds())
    h, rem = divmod(total_seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}h {m:02d}m {s:02d}s"


def _check_ollama():
    """Verifica que Ollama responda, lo intenta arrancar si no."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        if r.status_code == 200:
            return True
    except requests.ConnectionError:
        log.warning("Ollama no responde — intentando arrancar…")
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Esperar hasta 15s a que arranque
            for _ in range(30):
                time.sleep(0.5)
                try:
                    r2 = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=2)
                    if r2.status_code == 200:
                        log.info("Ollama arrancado correctamente")
                        return True
                except requests.ConnectionError:
                    continue
            log.error("No se pudo arrancar Ollama tras 15s")
            return False
        except FileNotFoundError:
            log.error("Comando 'ollama' no encontrado en PATH")
            return False
    except Exception as exc:
        log.error("Error comprobando Ollama: %s", exc)
        return False
    return False


def _ollama_generate(model, prompt, system=None, stream=False):
    """Llama a /api/generate de Ollama."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
    }
    if system:
        payload["system"] = system

    log.info("→ POST /api/generate  model=%s  prompt_len=%d", model, len(prompt))
    r = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json=payload,
        timeout=OLLAMA_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def _ollama_chat(model, messages, stream=False):
    """Llama a /api/chat de Ollama."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }
    log.info("→ POST /api/chat  model=%s  msgs=%d", model, len(messages))
    r = requests.post(
        f"{OLLAMA_BASE}/api/chat",
        json=payload,
        timeout=OLLAMA_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "gpu": GPU_LABEL,
        "models": AVAILABLE_MODELS,
        "uptime": _uptime(),
    })


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    model = data.get("model", DEFAULT_MODEL)
    prompt = data.get("prompt", "")
    system = data.get("system", None)

    if not prompt:
        return jsonify({"error": "campo 'prompt' requerido"}), 400

    try:
        result = _ollama_generate(model, prompt, system)
        return jsonify({
            "model": model,
            "response": result.get("response", ""),
            "done": result.get("done", True),
        })
    except requests.exceptions.Timeout:
        log.error("Timeout en generate (%ds) para %s", OLLAMA_TIMEOUT, model)
        return jsonify({"error": "timeout", "model": model}), 504
    except requests.exceptions.RequestException as exc:
        log.error("Error en generate: %s", exc)
        return jsonify({"error": str(exc)}), 502


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    model = data.get("model", DEFAULT_MODEL)
    messages = data.get("messages", [])

    if not messages:
        return jsonify({"error": "campo 'messages' requerido"}), 400

    try:
        result = _ollama_chat(model, messages)
        return jsonify({
            "model": model,
            "message": result.get("message", {}),
            "done": result.get("done", True),
        })
    except requests.exceptions.Timeout:
        log.error("Timeout en chat (%ds) para %s", OLLAMA_TIMEOUT, model)
        return jsonify({"error": "timeout", "model": model}), 504
    except requests.exceptions.RequestException as exc:
        log.error("Error en chat: %s", exc)
        return jsonify({"error": str(exc)}), 502


# ── Endpoints específicos CertificadoYa ────────────────────────────────────

PRESUPUESTO_SYSTEM = (
    "Eres un asistente experto en eficiencia energética y certificados energéticos en España. "
    "Genera un presupuesto orientativo realista para un Certificado de Eficiencia Energética (CEE). "
    "Responde en español, con un formato claro:\n\n"
    "Presupuesto Orientativo:\n"
    "- Tipo de inmueble: ...\n"
    "- Superficie: ... m²\n"
    "- Código Postal: ...\n"
    "- Precio estimado: ... €\n"
    "- Incluye: visita, mediciones, emisión del certificado, registro.\n"
    "- Plazo estimado: ...\n"
    "- Notas adicionales si aplican (vivienda unifamiliar vs piso, etc.)\n\n"
    "Precios de referencia (2026):\n"
    "- Pisos <80m²: 80-120€\n"
    "- Pisos 80-120m²: 100-150€\n"
    "- Casas unifamiliares: 120-200€\n"
    "- Locales comerciales: 150-250€\n"
    "Ajusta según el tipo y la ubicación (comunidad autónoma)."
)


@app.route("/generar-presupuesto", methods=["POST"])
def generar_presupuesto():
    data = request.get_json(force=True)
    m2 = data.get("m2", "")
    tipo = data.get("tipo", "piso")
    cp = data.get("cp", "")
    direccion = data.get("direccion", "")
    notas = data.get("notas", "")
    model = data.get("model", DEFAULT_MODEL)

    prompt = (
        f"Genera un presupuesto orientativo para Certificado de Eficiencia Energética.\n"
        f"Tipo de inmueble: {tipo}\n"
        f"Superficie: {m2} m²\n"
        f"Código Postal: {cp}\n"
        f"Dirección: {direccion}\n"
        f"Notas adicionales: {notas}\n"
    )

    try:
        result = _ollama_generate(model, prompt, system=PRESUPUESTO_SYSTEM)
        return jsonify({
            "model": model,
            "presupuesto": result.get("response", ""),
        })
    except requests.exceptions.RequestException as exc:
        log.error("Error en generar-presupuesto: %s", exc)
        return jsonify({"error": str(exc)}), 502


FAQ_SYSTEM = (
    "Eres un asistente experto en Certificados de Eficiencia Energética (CEE) en España. "
    "Responde preguntas frecuentes de forma clara, precisa y en español. "
    "Basate en la normativa vigente (RD 390/2021, Directiva 2010/31/UE). "
    "Si no sabes la respuesta, indica que consulten a un técnico especializado."
)


@app.route("/responder-faq", methods=["POST"])
def responder_faq():
    data = request.get_json(force=True)
    pregunta = data.get("pregunta", "")
    model = data.get("model", DEFAULT_MODEL)

    if not pregunta:
        return jsonify({"error": "campo 'pregunta' requerido"}), 400

    try:
        result = _ollama_chat(model, [
            {"role": "system", "content": FAQ_SYSTEM},
            {"role": "user", "content": pregunta},
        ])
        msg = result.get("message", {})
        return jsonify({
            "model": model,
            "respuesta": msg.get("content", ""),
        })
    except requests.exceptions.RequestException as exc:
        log.error("Error en responder-faq: %s", exc)
        return jsonify({"error": str(exc)}), 502


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("=" * 60)
    log.info("CertificadoYa — Servicio de Modelos Locales")
    log.info("GPU: %s", GPU_LABEL)
    log.info("Puerto: %d", PORT)
    log.info("Modelos: %s", ", ".join(AVAILABLE_MODELS))
    log.info("=" * 60)

    if not _check_ollama():
        log.error("Ollama no está disponible. Saliendo.")
        sys.exit(1)

    log.info("Ollama OK → sirviendo en http://%s:%d", HOST, PORT)
    app.run(host=HOST, port=PORT, debug=False)
