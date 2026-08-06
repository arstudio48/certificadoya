#!/usr/bin/env python3
"""
CertificadoYa — Limpieza de registros de test
Marca leads y técnicos de prueba con es_test=True para filtrarlos siempre.
NO los borra (por si hay que auditar), solo los aísla.
"""
from supabase import create_client

URL = "https://wypgqpgjlookbhuaiyxa.supabase.co"
KEY = "sb_secret_7LGmViutdXYU16hwvAqlJg_hZjhfcLe"
sb = create_client(URL, KEY)

def es_test(valor):
    if not valor:
        return False
    return 'test' in str(valor).lower()

# 1. Leads de test
leads = sb.table("leads").select("*").execute().data
tests_l = [l for l in leads if es_test(l.get('nombre_cliente')) or es_test(l.get('email_cliente'))]
for l in tests_l:
    sb.table("leads").update({"es_test": True}).eq("id", l["id"]).execute()
print(f"✓ {len(tests_l)} leads marcados como test")

# 2. Técnicos de test
tecs = sb.table("tecnicos").select("*").execute().data
tests_t = [t for t in tecs if es_test(t.get('nombre'))]
for t in tests_t:
    sb.table("tecnicos").update({"es_test": True, "activo": False}).eq("id", t["id"]).execute()
print(f"✓ {len(tests_t)} técnicos marcados como test (y desactivados)")

print("\nLimpieza completada. Los registros de test ya no aparecerán en notificaciones ni asignaciones.")
