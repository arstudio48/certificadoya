#!/usr/bin/env python3
"""bienvenida_nuevos.py — Envía emails de bienvenida a altas de las últimas 24h.
Técnicos nuevos (bienvenida-tecnico) y clientes nuevos con pago (bienvenida-cliente).
Usa las Edge Functions de Supabase. Variables de entorno: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY.
"""
import os, json, urllib.request, urllib.error

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

def llamar(func: str) -> dict:
    url = f"{SUPABASE_URL}/functions/v1/{func}"
    req = urllib.request.Request(url, data=json.dumps({"todos": True}).encode(),
                                  headers={"Authorization": f"Bearer {KEY}",
                                           "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)[:200]}

if __name__ == "__main__":
    if not SUPABASE_URL or not KEY:
        print("FALTAN SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY")
        raise SystemExit(1)
    t = llamar("bienvenida-tecnico")
    c = llamar("bienvenida-cliente")
    tec = t.get("enviados", "ERR") if isinstance(t, dict) else "ERR"
    cli = c.get("enviados", "ERR") if isinstance(c, dict) else "ERR"
    print(f"Técnicos bienvenidos: {tec}")
    print(f"Clientes bienvenidos: {cli}")
    if t.get("detalle"):
        fallos_t = [x for x in t["detalle"] if not x.get("ok")]
        if fallos_t: print(f"  Fallos técnicos: {len(fallos_t)}")
    if c.get("detalle"):
        fallos_c = [x for x in c["detalle"] if not x.get("ok")]
        if fallos_c: print(f"  Fallos clientes: {len(fallos_c)}")
