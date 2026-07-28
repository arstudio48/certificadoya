#!/usr/bin/env python3
"""
Activar tecnicos FP cuando el RD 659/2025 entre en vigor.
Ejecutar manualmente (o via cron con chequeo de noticias) cuando:
  - Sea final de mes (24 jul 2026 en adelante) O
  - Las noticias oficiales (MITECO/BOE) indiquen que ya se puede firmar CEE como FP.
Pone puede_ejercer=True a todos los tecnicos es_fp=True para que auto_assign
empiece a asignarles leads.
"""
import os, sys
from datetime import datetime, timezone
_site = [p for p in sys.path if 'site-packages' in p]
if _site: sys.path.insert(0, _site[0])
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()
URL = os.environ.get("SUPABASE_URL", "https://wypgqpgjlookbhuaiyxa.supabase.co")
KEY = os.environ.get("SUPABASE_SERVICE_KEY")
supabase = create_client(URL, KEY)

def activar():
    r = supabase.table("tecnicos").update({"puede_ejercer": True}) \
        .eq("es_fp", True).eq("puede_ejercer", False).execute()
    n = len(r.data or [])
    print(f"{datetime.now()} - FP activados para ejercer: {n}")
    return n

if __name__ == "__main__":
    activar()
