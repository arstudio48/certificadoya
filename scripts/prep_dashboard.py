import json

# ---- Datos reales extraídos 01-08-2026 ----
gsc = json.load(open('C:/Users/artur/AppData/Local/hermes/scripts/gsc_data.json'))
gc = json.load(open('C:/Users/artur/AppData/Local/hermes/scripts/analitica_historico.json'))

# Evolución GSC (70 días con datos)
ev = gsc['por_dia']
labels = [x['fecha'][5:] for x in ev]
imp = [x['impresiones'] for x in ev]
clicks = [x['clics'] for x in ev]

# GoatCounter sesiones
gc_ev = gc['evolucion_diaria']
gc_labels = [x['day'][5:] for x in gc_ev]
gc_ses = [x.get('sesiones') or 0 for x in gc_ev]

# Top queries y páginas
tq = gsc['top_queries'][:12]
tp = gsc['top_paginas'][:10]

# Leads
leads_total = 60
leads_estados = {'pendientes': 2, 'asignados': 35, 'pagados': 0, 'cancelados': 0}
leads_prov = [('Madrid', 19), ('Asturias', 14), ('Barcelona', 4), ('Gipuzkoa', 5), ('Bizkaia', 3),
              ('Navarra', 2), ('Valencia', 2), ('Jaén', 2), ('Sin definir', 2), ('Almería', 1),
              ('Gijón', 1), ('Tenerife', 1)]
leads_fuente = [('web', 50), ('calculadora', 2), ('stripe', 1), ('reserva contra entrega', 1), ('tests', 6)]
leads_inmueble = [('piso', 46), ('unifamiliar', 8), ('adosado', 3), ('local', 2), ('casa', 1)]

# Técnicos
tecnicos = {'supabase_activos': 18, 'master_universo': 1148, 'pendientes_email': 944, 'historial_enviados': 398}

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
print('dashboard_data.json OK:', len(labels), 'dias GSC,', len(gc_ev), 'dias GC')
