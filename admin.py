#!/usr/bin/env python3
"""
Panel de Administracion - CertificadoYA
Gestion de leads, tecnicos y comisiones desde terminal
"""
import os
import sys
from datetime import datetime
from supabase import create_client

URL = "https://wypgqpgjlookbhuaiyxa.supabase.co"
KEY = "sb_secret_7LGmViutdXYU16hwvAqlJg_hZjhfcLe"

supabase = create_client(URL, KEY)

# ─── COLORES ───
G = '\033[92m'  # green
Y = '\033[93m'  # yellow
R = '\033[91m'  # red
B = '\033[94m'  # blue
C = '\033[96m'  # cyan
W = '\033[0m'   # reset
BOLD = '\033[1m'

ESTADOS = {
    'nuevo': '🆕 Nuevo',
    'asignado': '👷 Asignado',
    'contactado': '📞 Contactado',
    'presupuestado': '📋 Presupuestado',
    'completado': '✅ Completado',
    'cancelado': '❌ Cancelado'
}

def listar_leads(estado=None):
    """Listar todos los leads, opcionalmente filtrados por estado"""
    query = supabase.table('leads').select('*').order('created_at', desc=True)
    if estado:
        query = query.eq('estado', estado)
    result = query.execute()

    if not result.data:
        print(f"{Y}No hay leads{' con estado ' + estado if estado else ''}{W}")
        return

    print(f"\n{BOLD}{'='*80}{W}")
    print(f"{BOLD}  LEADS - CertificadoYa{W}  ({len(result.data)} total)")
    print(f"{BOLD}{'='*80}{W}")

    for lead in result.data:
        estado_icono = ESTADOS.get(lead.get('estado'), lead.get('estado','?'))
        created = lead.get('created_at','')[:19].replace('T',' ')
        print(f"\n  {B}{lead['id'][:8]}{W} | {estado_icono} | {created}")
        print(f"  {BOLD}{lead['nombre_cliente']}{W} | 📞 {lead.get('telefono_cliente','?')} | 📧 {lead.get('email_cliente','-')}")
        print(f"  📍 CP: {lead.get('codigo_postal','?')} | {lead.get('ciudad','?')} | {lead.get('m2','?')}m² | {lead.get('tipo_inmueble','?')}")
        print(f"  💰 {lead.get('presupuesto_min','?')}€ - {lead.get('presupuesto_max','?')}€ | Fuente: {lead.get('fuente','web')}")

def cambiar_estado(lead_id, nuevo_estado):
    """Cambiar el estado de un lead"""
    if nuevo_estado not in ESTADOS:
        print(f"{R}Estado invalido. Usa: {', '.join(ESTADOS.keys())}{W}")
        return

    result = supabase.table('leads').update({
        'estado': nuevo_estado,
        'updated_at': datetime.utcnow().isoformat()
    }).eq('id', lead_id).execute()

    if result.data:
        print(f"{G}Lead {lead_id[:8]} -> {ESTADOS[nuevo_estado]}{W}")
    else:
        print(f"{R}Lead no encontrado{W}")

def listar_tecnicos():
    """Listar tecnicos registrados"""
    result = supabase.table('tecnicos').select('*').order('created_at', desc=True).execute()

    if not result.data:
        print(f"{Y}No hay tecnicos registrados{W}")
        return

    print(f"\n{BOLD}{'='*80}{W}")
    print(f"{BOLD}  TECNICOS{W}  ({len(result.data)} total)")
    print(f"{BOLD}{'='*80}{W}")

    for t in result.data:
        verif = '✅' if t.get('verificado') else '⏳'
        print(f"\n  {verif} {BOLD}{t['nombre']} {t.get('apellidos','')}{W}")
        print(f"  📧 {t.get('email','?')} | 📞 {t.get('telefono','?')} | {t.get('titulacion','?')}")
        print(f"  📍 {t.get('provincia','?')} | CP: {t.get('cp_cobertura',[])}")

def stats():
    """Estadisticas rapidas"""
    total = supabase.table('leads').select('*', count='exact').eq('estado','nuevo').execute()
    asignados = supabase.table('leads').select('*', count='exact').eq('estado','asignado').execute()
    completados = supabase.table('leads').select('*', count='exact').eq('estado','completado').execute()
    tecnicos = supabase.table('tecnicos').select('*', count='exact').execute()

    print(f"\n{BOLD}📊 ESTADISTICAS{W}")
    print(f"  🆕 Nuevos:      {total.count}")
    print(f"  👷 Asignados:    {asignados.count}")
    print(f"  ✅ Completados:  {completados.count}")
    print(f"  👨‍🔧 Tecnicos:     {tecnicos.count}")

def help():
    print(f"""
{BOLD}CERTIFICADOYA - Panel de Administracion{W}

  {G}python admin.py {B}leads{W}              Ver todos los leads
  {G}python admin.py {B}leads nuevo{W}         Ver leads nuevos
  {G}python admin.py {B}asignar <id> {W}       Cambiar estado a 'asignado'
  {G}python admin.py {B}contactar <id> {W}     Cambiar a 'contactado'
  {G}python admin.py {B}completar <id> {W}     Cambiar a 'completado'
  {G}python admin.py {B}cancelar <id> {W}      Cambiar a 'cancelado'
  {G}python admin.py {B}estado <id> <e>{W}     Cambiar a estado personalizado
  {G}python admin.py {B}tecnicos{W}            Listar tecnicos
  {G}python admin.py {B}stats{W}               Estadisticas rapidas
""")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        help()
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == 'leads':
        estado = sys.argv[2] if len(sys.argv) > 2 else None
        listar_leads(estado)
    elif cmd == 'asignar' and len(sys.argv) > 2:
        cambiar_estado(sys.argv[2], 'asignado')
    elif cmd == 'contactar' and len(sys.argv) > 2:
        cambiar_estado(sys.argv[2], 'contactado')
    elif cmd == 'completar' and len(sys.argv) > 2:
        cambiar_estado(sys.argv[2], 'completado')
    elif cmd == 'cancelar' and len(sys.argv) > 2:
        cambiar_estado(sys.argv[2], 'cancelado')
    elif cmd == 'estado' and len(sys.argv) > 3:
        cambiar_estado(sys.argv[2], sys.argv[3])
    elif cmd == 'tecnicos':
        listar_tecnicos()
    elif cmd == 'stats':
        stats()
    else:
        help()
