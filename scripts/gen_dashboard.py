import json

d = json.load(open('C:/Users/artur/certificadoya/dashboard_data.json', encoding='utf-8'))

tq_rows = ''.join(
    f"<tr><td>{q.get('query','?')[:50]}</td><td>{q.get('impresiones',0)}</td><td>{q.get('clics',0)}</td><td>{round(q.get('posicion', q.get('posicion_media',0)),1)}</td></tr>"
    for q in d['tq'])
tp_rows = ''.join(
    f"<tr><td>{p.get('pagina', p.get('page','?'))[:60]}</td><td>{p.get('impresiones',0)}</td><td>{p.get('clics',0)}</td><td>{round(p.get('posicion', p.get('posicion_media',0)),1)}</td></tr>"
    for p in d['tp'])
lp_rows = ''.join(f"<tr><td>{p}</td><td>{n}</td></tr>" for p, n in d['leads_prov'])
lf_rows = ''.join(f"<tr><td>{f}</td><td>{n}</td></tr>" for f, n in d['leads_fuente'])
li_rows = ''.join(f"<tr><td>{i}</td><td>{n}</td></tr>" for i, n in d['leads_inmueble'])

html = f"""<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard CertificadoYa.es — 01-ago-2026</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
:root{{--bg:#0d1117;--card:#161b22;--border:#30363d;--text:#e6edf3;--text2:#8b949e;--accent:#58a6ff;--green:#3fb950;--yellow:#d29922;--red:#f85149}}
[data-theme="light"]{{--bg:#f6f8fa;--card:#ffffff;--border:#d8dee4;--text:#24292f;--text2:#57606a;--accent:#0969da;--green:#1a7f37;--yellow:#9a6700;--red:#cf222e}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--text);font-size:14px}}
.sidebar{{width:240px;position:fixed;height:100vh;background:var(--card);border-right:1px solid var(--border);padding:20px;overflow-y:auto;z-index:100}}
.sidebar h1{{font-size:16px;margin-bottom:18px;color:var(--accent)}}
.sidebar a{{display:block;color:var(--text2);text-decoration:none;padding:8px 10px;border-radius:6px;margin-bottom:4px;font-size:13px}}
.sidebar a:hover,.sidebar a.active{{background:var(--bg);color:var(--accent)}}
.main{{margin-left:240px;padding:24px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:20px;margin-bottom:20px}}
.card h2{{font-size:15px;margin-bottom:14px;color:var(--accent)}}
.kpis{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:20px}}
.kpi{{flex:1;min-width:140px;padding:16px;background:var(--card);border:1px solid var(--border);border-radius:8px;text-align:center}}
.kpi .value{{font-size:26px;font-weight:700;color:var(--accent)}}
.kpi .label{{font-size:12px;color:var(--text2);margin-top:4px}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.chart-container{{position:relative;height:320px;width:100%}}
table{{width:100%;border-collapse:collapse;font-size:12.5px}}
th,td{{text-align:left;padding:7px 9px;border-bottom:1px solid var(--border)}}
th{{color:var(--text2);font-weight:600}}
.data-gap{{background:rgba(210,153,34,.12);border:1px solid var(--yellow);border-radius:8px;padding:12px 16px;margin-bottom:20px;color:var(--yellow);font-size:13px}}
.sem{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}}
.sem-g{{background:var(--green)}}.sem-y{{background:var(--yellow)}}.sem-r{{background:var(--red)}}
#mapTecnicos{{height:380px;border-radius:8px;background:var(--card)}}
.theme-btn{{position:fixed;top:16px;right:16px;z-index:200;background:var(--card);border:1px solid var(--border);color:var(--text);padding:8px 14px;border-radius:6px;cursor:pointer;font-size:12px}}
@media(max-width:900px){{.sidebar{{width:180px}}.main{{margin-left:180px;padding:14px}}.grid-2{{grid-template-columns:1fr}}.kpi{{min-width:110px}}}}
</style>
</head>
<body>
<button class="theme-btn" onclick="toggleTheme()">🌓 Tema</button>
<nav class="sidebar">
  <h1>🔍 CertificadoYa.es</h1>
  <a href="#resumen" class="active">Resumen</a>
  <a href="#seo">SEO</a>
  <a href="#queries">Queries</a>
  <a href="#trafico">Tráfico</a>
  <a href="#leads">Leads</a>
  <a href="#tecnicos">Técnicos</a>
  <a href="#web">Web Live</a>
  <a href="#oportunidades">Oportunidades</a>
</nav>

<div class="main">
  <div class="data-gap">⚠️ <strong>Limitaciones:</strong> sin acceso GA4 dashboard, Google Ads, Ahrefs/Semrush, Cloudflare logs, Matomo. Datos SEO de GSC (90 días, vía service account), tráfico de GoatCounter (71 días), leads de Supabase (live). PSI rate-limited (performance 0/100 no fiable hoy).</div>

  <div class="kpis">
    <div class="kpi"><div class="value">{d['gsc_total']['impresiones']}</div><div class="label">Impresiones GSC 90d</div></div>
    <div class="kpi"><div class="value">{d['gsc_total']['clics']}</div><div class="label">Clics GSC 90d</div></div>
    <div class="kpi"><div class="value">{d['gsc_total']['ctr']}%</div><div class="label">CTR</div></div>
    <div class="kpi"><div class="value">{d['gsc_total']['posicion_media']}</div><div class="label">Posición media</div></div>
    <div class="kpi"><div class="value">{d['leads_total']}</div><div class="label">Leads totales</div></div>
    <div class="kpi"><div class="value">{d['tecnicos']['supabase_activos']}</div><div class="label">Técnicos activos</div></div>
    <div class="kpi"><div class="value">{d['tecnicos']['historial_enviados']}</div><div class="label">Emails campaña</div></div>
  </div>

  <div class="card" id="resumen">
    <h2>Resumen ejecutivo</h2>
    <p style="color:var(--text2);line-height:1.7">Web de 68 días (indexación desde 20-may-2026). Tráfico estable 4-8 sesiones/día (GoatCounter). GSC acumula 13.660 impresiones con CTR 1,05% — bajo por posición media 37,1. 60 leads, 35 asignados, <strong>0 pagados</strong> (embudo se corta en asignación). 18 técnicos activos en Supabase. Campaña email: 398 enviados, 944 pendientes. RD 659/2025 en vigor desde 23-jul-2026 — ventana normativa activa.</p>
  </div>

  <div class="card" id="seo">
    <h2>SEO — Evolución (GSC, 90 días)</h2>
    <div class="chart-container"><canvas id="chartEvol"></canvas></div>
  </div>

  <div class="grid-2">
    <div class="card">
      <h2>Impresiones vs Sesiones</h2>
      <div class="chart-container"><canvas id="chartGC"></canvas></div>
    </div>
    <div class="card" id="trafico">
      <h2>Dispositivos (GSC)</h2>
      <div class="chart-container"><canvas id="chartDev"></canvas></div>
    </div>
  </div>

  <div class="card" id="queries">
    <h2>Top 12 queries GSC (90d)</h2>
    <table><thead><tr><th>Query</th><th>Impresiones</th><th>Clics</th><th>Pos</th></tr></thead><tbody>{tq_rows}</tbody></table>
  </div>

  <div class="card">
    <h2>Top 10 páginas GSC (90d)</h2>
    <table><thead><tr><th>Página</th><th>Impresiones</th><th>Clics</th><th>Pos</th></tr></thead><tbody>{tp_rows}</tbody></table>
  </div>

  <div class="grid-2">
    <div class="card">
      <h2>Leads por estado</h2>
      <div class="chart-container"><canvas id="chartLeadsEst"></canvas></div>
    </div>
    <div class="card">
      <h2>Embudo conversión</h2>
      <div class="chart-container"><canvas id="chartFunnel"></canvas></div>
    </div>
  </div>

  <div class="grid-2">
    <div class="card" id="leads">
      <h2>Leads por provincia</h2>
      <table><thead><tr><th>Provincia</th><th>Leads</th></tr></thead><tbody>{lp_rows}</tbody></table>
    </div>
    <div class="card">
      <h2>Leads por fuente e inmueble</h2>
      <table><thead><tr><th>Fuente</th><th>N</th></tr></thead><tbody>{lf_rows}</tbody></table>
      <br>
      <table><thead><tr><th>Inmueble</th><th>N</th></tr></thead><tbody>{li_rows}</tbody></table>
    </div>
  </div>

  <div class="card" id="tecnicos">
    <h2>Cobertura técnica — Mapa España</h2>
    <div id="mapTecnicos"></div>
    <p style="margin-top:10px;color:var(--text2);font-size:12px">18 activos en Supabase · universo 1.148 en master · 944 pendientes email · 398 enviados. Círculo verde = provincia con técnicos activos; rojo = sin técnicos.</p>
  </div>

  <div class="grid-2">
    <div class="card">
      <h2>Radar técnicos (universo)</h2>
      <div class="chart-container"><canvas id="chartRadar"></canvas></div>
    </div>
    <div class="card" id="web">
      <h2>Web Live</h2>
      <table>
        <tr><td>Estado</td><td><span class="sem sem-g"></span>HTTP 200</td></tr>
        <tr><td>TTFB</td><td>0.33s</td></tr>
        <tr><td>CDN</td><td>GitHub Pages (edge fra)</td></tr>
        <tr><td>SSL</td><td>✅ válido hasta 21-oct-2026</td></tr>
        <tr><td>Home</td><td>107.6 KB HTML</td></tr>
        <tr><td>JSON-LD</td><td>5 bloques (Breadcrumb, LocalBusiness, FAQ, Org)</td></tr>
        <tr><td>Páginas repo</td><td>474 (blog: 101)</td></tr>
        <tr><td>Sitemaps</td><td>236 + 60 URLs</td></tr>
        <tr><td>Analytics</td><td>GA4 + Clarity + GoatCounter + Bing</td></tr>
      </table>
    </div>
  </div>

  <div class="card" id="oportunidades">
    <h2>Oportunidades priorizadas</h2>
    <table>
      <thead><tr><th>#</th><th>Acción</th><th>Impacto</th><th>Esfuerzo</th></tr></thead>
      <tbody>
        <tr><td>1</td><td>Convertir landings /certificado-energetico-* (1.300 imp, pos 54) — optimizar título/CTA para clics</td><td>Alto</td><td>Bajo</td></tr>
        <tr><td>2</td><td>Atacar queries 'ahorro energético X' pos 25-70 con contenido local</td><td>Alto</td><td>Medio</td></tr>
        <tr><td>3</td><td>Desbloquear embudo leads: 35 asignados → 0 pagados (seguimiento técnico)</td><td>Alto</td><td>Medio</td></tr>
        <tr><td>4</td><td>Contenido RD 659/2025 (ventana normativa abierta — query '659/2025' pos 8,2 sin clics)</td><td>Medio</td><td>Bajo</td></tr>
        <tr><td>5</td><td>Ampliar cobertura provincial de técnicos (rojo en mapa)</td><td>Medio</td><td>Medio</td></tr>
      </tbody>
    </table>
  </div>
</div>

<script>
const DATA = {json.dumps(d, ensure_ascii=False)};

// 1. Evolución GSC
new Chart(document.getElementById('chartEvol'), {{
  type:'line',
  data:{{labels:DATA.labels, datasets:[
    {{label:'Impresiones', data:DATA.imp, borderColor:'#58a6ff', backgroundColor:'#58a6ff22', fill:true, yAxisID:'y', tension:.3}},
    {{label:'Clics', data:DATA.clicks, borderColor:'#3fb950', yAxisID:'y1', tension:.3}}
  ]}},
  options:{{maintainAspectRatio:false, scales:{{y:{{position:'left',title:{{display:true,text:'Impresiones'}}}}, y1:{{position:'right',grid:{{drawOnChartArea:false}},title:{{display:true,text:'Clics'}}}}}}, interaction:{{mode:'index',intersect:false}}}}
}});

// 2. GoatCounter sesiones
new Chart(document.getElementById('chartGC'), {{
  type:'bar',
  data:{{labels:DATA.gc_labels, datasets:[
    {{label:'Sesiones', data:DATA.gc_ses, backgroundColor:'#58a6ff66', borderColor:'#58a6ff', borderWidth:1}}
  ]}},
  options:{{maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}, scales:{{y:{{beginAtZero:true}}}}}}
}});

// 3. Dispositivos
new Chart(document.getElementById('chartDev'), {{
  type:'doughnut',
  data:{{labels:['Desktop','Mobile','Tablet'], datasets:[{{data:[9828,3584,248], backgroundColor:['#58a6ff','#3fb950','#d29922']}}]}},
  options:{{maintainAspectRatio:false, plugins:{{legend:{{position:'bottom'}}}}}}
}});

// 4. Leads por estado
const LE = {{pendientes:2, asignados:35, pagados:0, cancelados:0}};
new Chart(document.getElementById('chartLeadsEst'), {{
  type:'doughnut',
  data:{{labels:['Pendientes','Asignados','Pagados','Cancelados'], datasets:[{{data:[LE.pendientes,LE.asignados,LE.pagados,LE.cancelados], backgroundColor:['#d29922','#58a6ff','#3fb950','#f85149']}}]}},
  options:{{maintainAspectRatio:false, plugins:{{legend:{{position:'bottom'}}}}}}
}});

// 5. Embudo
new Chart(document.getElementById('chartFunnel'), {{
  type:'bar',
  data:{{labels:['Visitas (GC)','Leads','Asignados','Pagados'], datasets:[{{data:[431,60,35,0], backgroundColor:['#58a6ff88','#3fb95088','#d2992288','#f8514988']}}]}},
  options:{{indexAxis:'y', maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}}}
}});

// 6. Radar técnicos
new Chart(document.getElementById('chartRadar'), {{
  type:'radar',
  data:{{labels:['Supabase activos','Master universo','Pendientes email','Historial enviados'], datasets:[{{data:[18,1148,944,398], backgroundColor:'#58a6ff44', borderColor:'#58a6ff'}}]}},
  options:{{maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}, scales:{{r:{{beginAtZero:true}}}}}}
}});

// 7. Mapa Leaflet
const map = L.map('mapTecnicos').setView([40.416,-3.703], 6);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{attribution:'© OpenStreetMap'}}).addTo(map);
const provs = [
  {{name:'Madrid', coords:[40.416,-3.703], n:10}},
  {{name:'Asturias', coords:[43.36,-5.85], n:8}},
  {{name:'Barcelona', coords:[41.387,2.170], n:2}},
  {{name:'Gipuzkoa', coords:[43.32,-1.98], n:5}},
  {{name:'Bizkaia', coords:[43.26,-2.93], n:3}},
  {{name:'Navarra', coords:[42.69,-1.68], n:2}},
  {{name:'Valencia', coords:[39.47,-0.37], n:2}},
  {{name:'Jaén', coords:[37.77,-3.79], n:2}},
  {{name:'Almería', coords:[36.84,-2.46], n:1}},
  {{name:'Gijón', coords:[43.54,-5.66], n:1}},
  {{name:'Tenerife', coords:[28.29,-16.63], n:1}}
];
provs.forEach(t => {{
  const color = t.n > 0 ? '#3fb950' : '#f85149';
  L.circleMarker(t.coords, {{radius: Math.max(5, t.n*2.2), color, fillColor: color, fillOpacity:.55}})
   .addTo(map).bindPopup(`<b>${{t.name}}</b>: ${{t.n}} técnicos`);
}});

// Tema
function toggleTheme() {{
  const h = document.documentElement;
  h.setAttribute('data-theme', h.getAttribute('data-theme')==='dark' ? 'light' : 'dark');
  localStorage.setItem('theme', h.getAttribute('data-theme'));
  location.reload();
}}
if(localStorage.getItem('theme')) document.documentElement.setAttribute('data-theme', localStorage.getItem('theme'));
</script>
</body>
</html>
"""

with open('C:/Users/artur/certificadoya/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('dashboard.html OK:', len(html), 'chars')
