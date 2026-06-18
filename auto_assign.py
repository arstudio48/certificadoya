#!/usr/bin/env python3
"""
CertificadoYA — Asignación automática de leads por código postal
Ejecutar periódicamente (cron) para asignar leads nuevos a técnicos.

Algoritmo:
  1. Obtener leads en estado 'nuevo'
  2. Para cada lead, buscar técnicos verificados/activos cuyo cp_cobertura
     contenga el prefijo de 3 dígitos del CP del lead
  3. Asignar con round-robin por zona (equilibra carga entre técnicos)
  4. NOTIFICAR al técnico asignado por email
  5. Si no hay técnico en la zona, NOTIFICAR al admin para acción manual
"""

import os
import sys
import smtplib
import json
from datetime import datetime, timezone
from collections import defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Fix import shadowing: local supabase/ dir conflicts with pip package
_site = [p for p in sys.path if 'site-packages' in p]
if _site:
    sys.path.insert(0, _site[0])
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

URL = os.environ.get("SUPABASE_URL", "https://wypgqpgjlookbhuaiyxa.supabase.co")
KEY = os.environ.get("SUPABASE_SERVICE_KEY")
if not KEY:
    print("ERROR: SUPABASE_SERVICE_KEY no está configurada.")
    sys.exit(1)

supabase = create_client(URL, KEY)

# Email config (Gmail SMTP)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "Artbriher@gmail.com"
SMTP_PASS = "wmyd dxmf awdezdeo"
ADMIN_EMAIL = "Artbriher@gmail.com"

# Emails a ignorar (pruebas del dueño)
SKIP_EMAILS = ["aparejado@me.com", "arturobriher@gmail.com"]


def enviar_email(destinatario: str, asunto: str, html: str):
    """Envía email vía Gmail SMTP."""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_USER
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(html, 'html', 'utf-8'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"  ⚠️ Error email a {destinatario}: {e}")
        return False


def mail_tecnico_asignado(lead, tecnico):
    """Email al técnico cuando se le asigna un lead."""
    zona = lead.get('provincia') or f"CP {lead.get('codigo_postal', '?')}"
    nombre = lead.get('nombre_cliente', '?')
    telefono = lead.get('telefono_cliente', '?')
    m2 = lead.get('m2', '?')
    tipo = lead.get('tipo_inmueble', 'piso')

    html = f"""<!DOCTYPE html>
<html><body style="font-family:Outfit,Arial,sans-serif;background:#f5f7f2;padding:20px">
<div style="max-width:600px;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden">
  <div style="background:linear-gradient(135deg,#1a5c2e,#2e8b47);padding:24px;text-align:center">
    <h1 style="color:#fff;margin:0;font-size:22px">✅ Nuevo lead asignado</h1>
    <p style="color:#b8d4a0;margin:4px 0 0;font-size:13px">CertificadoYa</p>
  </div>
  <div style="padding:24px">
    <p style="font-size:15px;color:#333">Hola <strong>{tecnico['nombre']}</strong>,</p>
    <p style="font-size:14px;color:#555;line-height:1.5">Se te ha asignado un nuevo cliente potencial en tu zona. <strong>Contacta con él lo antes posible.</strong></p>
    <div style="background:#f3f9eb;border-radius:8px;padding:16px;margin:16px 0">
      <p style="font-weight:600;color:#1a5c2e;margin:0 0 8px;font-size:13px">📋 Datos del cliente</p>
      <table style="width:100%;border-collapse:collapse;font-size:13px">
        <tr><td style="padding:4px 0;color:#666">Nombre</td><td style="padding:4px 0;color:#1a1a1a;font-weight:600">{nombre}</td></tr>
        <tr><td style="padding:4px 0;color:#666">Teléfono</td><td style="padding:4px 0;color:#1a1a1a"><a href="tel:{telefono}" style="color:#1a5c2e">{telefono}</a></td></tr>
        <tr><td style="padding:4px 0;color:#666">Zona</td><td style="padding:4px 0;color:#1a1a1a">{zona}</td></tr>
        <tr><td style="padding:4px 0;color:#666">Inmueble</td><td style="padding:4px 0;color:#1a1a1a">{m2} m² · {tipo}</td></tr>
      </table>
    </div>
    <p style="font-size:13px;color:#999;text-align:center">Si no puedes atender este lead, contacta con nosotros.</p>
  </div>
  <div style="padding:16px;text-align:center;font-size:12px;color:#999;border-top:1px solid #eee">
    <p style="margin:0">CertificadoYa · <a href="https://www.certificadoya.es" style="color:#1a5c2e">certificadoya.es</a></p>
  </div>
</div></body></html>"""
    return enviar_email(tecnico['email'], f"🔔 Nuevo lead asignado - {nombre}", html)


def mail_admin_sin_cobertura(lead):
    """Email al admin cuando un lead no tiene técnico disponible."""
    nombre = lead.get('nombre_cliente', '?')
    cp = lead.get('codigo_postal', '?')
    provincia = lead.get('provincia', '?')
    telefono = lead.get('telefono_cliente', '?')
    m2 = lead.get('m2', '?')

    html = f"""<!DOCTYPE html>
<html><body style="font-family:Outfit,Arial,sans-serif;background:#f5f7f2;padding:20px">
<div style="max-width:600px;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden">
  <div style="background:linear-gradient(135deg,#dc2626,#b91c1c);padding:24px;text-align:center">
    <h1 style="color:#fff;margin:0;font-size:22px">🟡 Lead sin técnico disponible</h1>
    <p style="color:#fca5a5;margin:4px 0 0;font-size:13px">Requiere acción manual</p>
  </div>
  <div style="padding:24px">
    <p style="font-size:15px;color:#333">Hay un nuevo lead en una zona <strong>sin técnicos verificados</strong>.</p>
    <div style="background:#fef2f2;border-radius:8px;padding:16px;margin:16px 0;border:1px solid #fecaca">
      <table style="width:100%;border-collapse:collapse;font-size:13px">
        <tr><td style="padding:4px 0;color:#666">Nombre</td><td style="padding:4px 0;color:#1a1a1a;font-weight:600">{nombre}</td></tr>
        <tr><td style="padding:4px 0;color:#666">Teléfono</td><td style="padding:4px 0;color:#1a1a1a"><a href="tel:{telefono}" style="color:#1a5c2e">{telefono}</a></td></tr>
        <tr><td style="padding:4px 0;color:#666">Zona</td><td style="padding:4px 0;color:#1a1a1a">{provincia} (CP {cp})</td></tr>
        <tr><td style="padding:4px 0;color:#666">Inmueble</td><td style="padding:4px 0;color:#1a1a1a">{m2} m²</td></tr>
      </table>
    </div>
    <p style="font-size:13px;color:#666">Acciones recomendadas:<br>
    1. Buscar técnico en esa provincia<br>
    2. Contactar al cliente directamente<br>
    3. Ampliar cobertura de técnicos existentes</p>
  </div>
  <div style="padding:16px;text-align:center;font-size:12px;color:#999;border-top:1px solid #eee">
    <p style="margin:0">CertificadoYa · <a href="https://www.certificadoya.es" style="color:#1a5c2e">certificadoya.es</a></p>
  </div>
</div></body></html>"""
    return enviar_email(ADMIN_EMAIL, f"🟡 Sin técnico para lead - {nombre} ({provincia})", html)


def mail_admin_asignado(lead, tecnico):
    """Email al admin confirmando asignación."""
    nombre = lead.get('nombre_cliente', '?')
    zona = lead.get('provincia') or f"CP {lead.get('codigo_postal', '?')}"
    html = f"""<p style="font-family:sans-serif">✅ Lead <strong>{nombre}</strong> ({zona}) asignado a <strong>{tecnico['nombre']}</strong>.</p>"""
    return enviar_email(ADMIN_EMAIL, f"✅ Lead asignado - {nombre}", html)


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
        print("[SILENT] No hay leads pendientes de asignar.")
        return 0, 0, 0

    print(f"🔍 {len(leads)} leads nuevos por asignar\n")

    asignados = 0
    sin_tecnico = 0
    ignorados = 0

    for lead in leads:
        email_lead = (lead.get('email_cliente') or '').lower().strip()

        # Saltar leads del dueño
        if email_lead in SKIP_EMAILS:
            print(f"⏭️  Ignorando lead propio: {lead.get('nombre_cliente', '?')} ({email_lead})")
            ignorados += 1
            continue

        cp = lead.get('codigo_postal', '')
        prefijo = cp[:3] if cp else '000'
        ciudad = lead.get('ciudad', lead.get('provincia', 'desconocida'))
        nombre = lead.get('nombre_cliente', '?')

        # 2. Buscar técnicos para este CP
        tecnicos = obtener_tecnicos_por_zona(prefijo)

        if not tecnicos:
            print(f"⚠️  Sin técnico para CP {cp} ({ciudad}) — {nombre}")
            sin_tecnico += 1
            if not dry_run:
                mail_admin_sin_cobertura(lead)
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

        # 4. Asignar en BD
        update = supabase.table('leads').update({
            'tecnico_asignado': mejor_tecnico['id'],
            'estado': 'asignado',
            'fecha_asignacion': datetime.now(timezone.utc).isoformat()
        }).eq('id', lead['id']).execute()

        if update.data:
            print(f"✅ {nombre} ({cp}, {ciudad}) → {mejor_tecnico['nombre']} (carga: {carga})")
            # Notificar al técnico
            mail_tecnico_asignado(lead, mejor_tecnico)
            # Notificar al admin
            mail_admin_asignado(lead, mejor_tecnico)
            asignados += 1
        else:
            print(f"❌ Error asignando {nombre}")

    print(f"\n📊 Resumen: {asignados} asignados, {sin_tecnico} sin técnico, {ignorados} ignorados")
    return asignados, sin_tecnico, ignorados


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv or '-n' in sys.argv
    asignar_leads(dry_run=dry)
