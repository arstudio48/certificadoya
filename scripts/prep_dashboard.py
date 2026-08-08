import json, subprocess, urllib.request
from collections import Counter

# ---- GSC + GoatCounter (JSON frescos generados por gsc_service.py / goatcounter-stats.py) ----
gsc = json.load(open('C:/Users/artur/AppData/Local/hermes/scripts/gsc_data.json'))
gc = json.load(open('C:/Users/artur/AppData/Local/hermes/scripts/analitica_historico.json'))

ev = gsc['por_dia']
labels = [x['fecha'][5:] for x in ev]
imp = [x['impresiones'] for x in ev]
clicks = [x['clics'] for x in ev]

gc_ev = gc['evolucion_diaria']
gc_labels = [x['day'][5:] for x in gc_ev]
gc_ses = [x.get('sesiones') or 0 for x in gc_ev]

tq = gsc['top_queries'][:12]
tp = gsc['top_paginas'][:10]

# ---- Leads en vivo desde Supabase REST ----
env_keys = {}
try:
    with open('C:/Users/artur/certificadoya/.env') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env_keys[k] = v
except Exception as e:
    print('WARN .env:', e)

supabase_url = env_keys.get('SUPABASE_URL', 'https://wypgqpgjlookbhuaiyxa.supabase.co')
service_key = env_keys.get('SUPABASE_SERVICE_KEY') or env_keys.get('SUPABASE_SERVICE_ROLE')

def sb_get(table, cols):
    url = f'{supabase_url}/rest/v1/{table}?select={cols}&limit=1000'
    req = urllib.request.Request(url, headers={
        'apikey': service_key, 'Authorization': f'Bearer {service_key}'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

leads = sb_get('leads', 'estado,fuente,provincia,tipo,m2,created_at')
leads_total = len(leads)
est_map = Counter((r.get('estado') or 'sin_estado') for r in leads)
# Normaliza estados a las claves del dashboard
est_norm = {'pendiente_tecnico': 'pendientes', 'pendiente': 'pendientes', 'nuevo': 'pendientes'}
leads_estados = {}
for k, v in est_map.items():
    key = est_norm.get(k, k)
    leads_estados[key] = leads_estados.get(key, 0) + v

lead_prov_raw = Counter((r.get('provincia') or 'Sin definir') for r in leads)
leads_prov = [(k, v) for k, v in lead_prov_raw.most_common()]

lead_fuente_raw = Counter((r.get('fuente') or 'web') for r in leads)
leads_fuente = [(k, v) for k, v in lead_fuente_raw.most_common()]

lead_inmueble_raw = Counter((r.get('tipo') or r.get('tipo_inmueble') or 'piso') for r in leads)
leads_inmueble = [(k, v) for k, v in lead_inmueble_raw.most_common()]

# ---- Técnicos en vivo ----
tec = sb_get('tecnicos', 'verificado,provincia')
tec_verif = sum(1 for r in tec if r.get('verificado') in (True, 'true', 1, 'True'))
tecnicos = {
    'supabase_activos': tec_verif,
    'master_universo': 1148,      # master CSV (universo captación, no cambia con web)
    'pendientes_email': 944,
    'historial_enviados': 398,
}

data = {
    'labels': labels, 'imp': imp, 'clicks': clicks,
    'gc_labels': gc_labels, 'gc_ses': gc_ses,
    'tq': tq, 'tp': tp,
    'leads_total': leads_total, 'leads_estados': leads_estados,
    'leads_prov': leads_prov, 'leads_fuente': leads_fuente, 'leads_inmueble': leads_inmueble,
    'tecnicos': tecnicos,
    'gsc_total': gsc['totales'],
}
with open('C:/Users/artur/certificadoya/dashboard_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print(f'dashboard_data.json OK: {len(labels)} dias GSC ({gsc["period"]}), {len(gc_ev)} dias GC, {leads_total} leads live, {tec_verif} tecnicos verificados')