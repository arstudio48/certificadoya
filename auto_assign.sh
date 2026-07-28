#!/usr/bin/env bash
# auto_assign.sh — Asignación automática de leads a técnicos (sin dependencias Python)
# CertificadoYa — 28 julio 2026
# Uso: bash auto_assign.sh

set -e

SUPABASE_URL="https://wypgqpgjlookbhuaiyxa.supabase.co"
ANON_KEY="sb_publishable_MsDx5jVGtDAzoB3l3-8DiQ_BxWpChA0"

# Leer SERVICE_ROLE_KEY del .env sin imprimir
SERVICE_KEY=$(grep SUPABASE_SERVICE_KEY .env 2>/dev/null | cut -d= -f2- | tr -d '"' | tr -d "'")
if [ -z "$SERVICE_KEY" ]; then
  echo "ERROR: SUPABASE_SERVICE_KEY no encontrada en .env"
  exit 1
fi

echo "=== AUTO-ASSIGN INICIADO ($(date -u +%Y-%m-%dT%H:%M:%SZ)) ==="

# 1. Obtener leads en estado 'nuevo'
LEADS=$(curl -s -H "apikey: $SERVICE_KEY" -H "Authorization: Bearer $SERVICE_KEY" \
  "$SUPABASE_URL/rest/v1/leads?estado=eq.nuevo&select=id,nombre_cliente,provincia,codigo_postal,telefono_cliente,email_cliente,m2,tipo_inmueble,presupuesto_min")

LEAD_COUNT=$(echo "$LEADS" | grep -o '"id"' | wc -l)
echo "Leads nuevos encontrados: $LEAD_COUNT"

if [ "$LEAD_COUNT" -eq 0 ]; then
  echo "No hay leads para asignar. Fin."
  exit 0
fi

# 2. Para cada lead, buscar técnico por provincia
echo "$LEADS" | python3 -c "
import sys, json, urllib.request, urllib.error

SUPABASE_URL = '$SUPABASE_URL'
SERVICE_KEY = '''$SERVICE_KEY'''

leads = json.load(sys.stdin)

def get_tecnicos(provincia):
    # La tabla tecnicos usa columna 'provincia' (texto con comas) y 'cp_cobertura' (array)
    # Buscamos técnicos cuyo campo provincia contenga la provincia del lead
    prov_lower = (provincia or '').lower()
    url = f'{SUPABASE_URL}/rest/v1/tecnicos?select=id,nombre,email,provincia,cp_cobertura,activo,verificado'
    req = urllib.request.Request(url, headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}'})
    try:
        with urllib.request.urlopen(req) as r:
            todos = json.load(r)
        # Filtrar por provincia que contenga el nombre (case-insensitive) y activo
        matched = [t for t in todos if t.get('activo') and prov_lower in (t.get('provincia') or '').lower()]
        return matched
    except Exception as e:
        return []

asignados = 0
for lead in leads:
    lid = lead.get('id')
    prov = lead.get('provincia')
    print(f'  Lead {lid[:8]}... provincia={prov}')
    tecnicos = get_tecnicos(prov)
    if tecnicos:
        t = tecnicos[0]
        print(f'    → Asignando a {t[\"nombre\"]} ({t[\"email\"]})')
        # Actualizar lead
        update = {'tecnico_asignado': t['id'], 'estado': 'pendiente_tecnico', 'fecha_asignacion': 'now()'}
        url = f'{SUPABASE_URL}/rest/v1/leads?id=eq.{lid}'
        req = urllib.request.Request(url, data=json.dumps(update).encode(), 
                                     headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}, method='PATCH')
        try:
            urllib.request.urlopen(req)
            asignados += 1
            print(f'    ✓ Asignado')
        except Exception as e:
            print(f'    ✗ Error: {e}')
    else:
        print(f'    ⚠ No hay técnico en {prov} — notificar admin')

print(f'Asignados: {asignados}/{len(leads)}')
"
