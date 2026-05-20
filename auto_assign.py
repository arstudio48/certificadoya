#!/usr/bin/env python3
"""
CertificadoYA — Asignación automática de leads por código postal
Ejecutar periódicamente (cron) para asignar leads nuevos a técnicos.

Algoritmo:
  1. Obtener leads en estado 'nuevo'
  2. Para cada lead, buscar técnicos verificados/activos cuyo cp_cobertura
     contenga el prefijo de 3 dígitos del CP del lead
  3. Asignar con round-robin por zona (equilibra carga entre técnicos)
  4. Si no hay técnico en la zona, el lead queda en 'nuevo' para revisión manual
"""

import sys
from datetime import datetime, timezone
from collections import defaultdict
from supabase import create_client

URL = "https://wypgqpgjlookbhuaiyxa.supabase.co"
KEY = "sb_secret_7LGmViutdXYU16hwvAqlJg_hZjhfcLe"

supabase = create_client(URL, KEY)


def obtener_tecnicos_por_zona(prefijo_cp: str) -> list:
    """Busca técnicos verificados y activos que cubran este prefijo CP (3 dígitos)"""
    result = supabase.table('tecnicos').select('*') \
        .eq('verificado', True) \
        .eq('activo', True) \
        .contains('cp_cobertura', [prefijo_cp]) \
        .execute()
    return result.data or []


def asignar_leads(dry_run: bool = False):
    """
    Asigna leads nuevos a técnicos disponibles.
    dry_run=True: solo muestra qué pasaría, sin modificar.
    """
    # 1. Obtener leads nuevos
    result = supabase.table('leads').select('*') \
        .eq('estado', 'nuevo') \
        .is_('tecnico_asignado', 'null') \
        .order('created_at', desc=False) \
        .execute()

    leads = result.data or []

    if not leads:
        print("✅ No hay leads pendientes de asignar.")
        return

    print(f"🔍 {len(leads)} leads nuevos por asignar\n")

    asignados = 0
    sin_tecnico = 0

    for lead in leads:
        cp = lead.get('codigo_postal', '')
        prefijo = cp[:3] if cp else '000'
        ciudad = lead.get('ciudad', 'desconocida')
        nombre = lead.get('nombre_cliente', '?')

        # 2. Buscar técnicos para este CP
        tecnicos = obtener_tecnicos_por_zona(prefijo)

        if not tecnicos:
            print(f"⚠️  Sin técnico para CP {cp} ({ciudad}) — {nombre}")
            sin_tecnico += 1
            continue

        # 3. Round-robin: elegir el técnico con menos leads activos en esta zona
        conteo = defaultdict(int)
        for t in tecnicos:
            r = supabase.table('leads').select('id', count='exact') \
                .eq('tecnico_asignado', t['id']) \
                .in_('estado', ['asignado', 'contactado', 'presupuestado']) \
                .execute()
            conteo[t['id']] = r.count

        # Elegir el técnico con menos carga
        mejor_tecnico = min(tecnicos, key=lambda t: conteo[t['id']])
        carga = conteo[mejor_tecnico['id']]

        if dry_run:
            print(f"   [DRY RUN] {nombre} ({cp}, {ciudad}) → {mejor_tecnico['nombre']} (carga: {carga})")
            asignados += 1
            continue

        # 4. Asignar
        update = supabase.table('leads').update({
            'tecnico_asignado': mejor_tecnico['id'],
            'estado': 'asignado',
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).eq('id', lead['id']).execute()

        if update.data:
            print(f"✅ {nombre} ({cp}, {ciudad}) → {mejor_tecnico['nombre']} (carga: {carga})")
            asignados += 1
        else:
            print(f"❌ Error asignando {nombre}")

    print(f"\n📊 Resumen: {asignados} asignados, {sin_tecnico} sin técnico")


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv or '-n' in sys.argv
    asignar_leads(dry_run=dry)
