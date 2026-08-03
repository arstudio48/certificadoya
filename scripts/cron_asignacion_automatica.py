import os, json, urllib.request

# Script de respaldo: asigna automáticamente todos los leads sin tecnico_asignado
# en estados 'nuevo', 'pendiente' o 'pendiente_tecnico'. Se ejecuta via cron cada minuto.
# Si ya tienen tecnico, la funcion lo detecta y no hace nada.

env_path = r"C:\Users\artur\certificadoya\.env"
token = ''
for line in open(env_path, encoding='utf-8'):
    if line.startswith('SUPABASE_SERVICE_KEY') or line.startswith('SUPABASE_SERVICE_ROLE'):
        token = line.split('=', 1)[1].strip().strip('"').strip("'")

if not token:
    print("ERROR: token no encontrado")
    raise SystemExit(1)

# Obtener leads pendientes sin tecnico
supa_url = "https://wypgqpgjlookbhuaiyxa.supabase.co/rest/v1/leads"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
    "apikey": token,
}
url = f"{supa_url}?select=id,provincia,estado,tecnico_asignado&estado=in.(nuevo,pendiente,pendiente_tecnico)&tecnico_asignado=is.null&es_test=eq.false"
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        leads = json.loads(r.read().decode())
except Exception as e:
    print("ERROR consultando leads:", str(e)[:300])
    raise SystemExit(1)

if not leads:
    print("OK: no hay leads pendientes sin asignar")
    raise SystemExit(0)

url_assign = "https://wypgqpgjlookbhuaiyxa.supabase.co/functions/v1/asignacion-automatica"
asignados = 0
fallidos = 0
for lead in leads:
    body = json.dumps({"leadId": lead["id"]}).encode()
    try:
        req = urllib.request.Request(url_assign, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        })
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read().decode())
            if resp.get("success"):
                asignados += 1
                print(f"  asignado {lead['id']} ({lead.get('provincia','?')}) -> {resp.get('tecnico_id','?')}")
            else:
                fallidos += 1
                print(f"  sin tecnico: {lead['id']} ({lead.get('provincia','?')})")
    except Exception as e:
        fallidos += 1
        print(f"  ERROR {lead['id']}: {str(e)[:200]}")

print(f"RESUMEN: {asignados} asignados, {fallidos} sin tecnico disponible")

# Solo imprimir si hubo asignaciones reales (para no spammear Telegram con "0 asignados")
if asignados > 0:
    print(f"\n✅ {asignados} lead(s) asignado(s) automáticamente en este ciclo.")
else:
    # Salida vacia -> el cron no_agent con deliver local no envia nada; con telegram no spamea
    import sys
    sys.exit(0)  # sin asignaciones: no generar output de aviso

