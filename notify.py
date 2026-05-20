#!/usr/bin/env python3
"""
CertificadoYA — Notificaciones por email
Envía emails al admin y a los técnicos cuando hay leads nuevos asignados.

Usa un archivo de estado local (last_notify.json) para evitar duplicados.
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from supabase import create_client

# Config
URL = "https://wypgqpgjlookbhuaiyxa.supabase.co"
KEY = "sb_secret_7LGmViutdXYU16hwvAqlJg_hZjhfcLe"
STATE_FILE = os.path.join(os.path.dirname(__file__), ".last_notify.json")

# SMTP Gmail
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "Artbriher@gmail.com"
SMTP_PASS = "wmyd dxmf awdezdeo"
ADMIN_EMAIL = "Artbriher@gmail.com"

supabase = create_client(URL, KEY)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_lead_id": None, "last_tecnico_id": None}


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


def send_email(to: str, subject: str, body_html: str) -> bool:
    """Envía email vía Gmail SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"CertificadoYa <{SMTP_USER}>"
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html', 'utf-8'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"  ❌ Error enviando a {to}: {e}")
        return False


def notify():
    state = load_state()
    last_lead_id = state.get('last_lead_id')

    # 1. Leads nuevos (no notificados al admin)
    query = supabase.table('leads').select('*, tecnicos!inner(nombre, email, telefono)') \
        .order('created_at', desc=False)

    if last_lead_id:
        # Solo leads posteriores al último notificado
        # Usamos un approach simple: traer todos los leads no notificados
        query = query.gt('created_at', state.get('last_check_time', '2000-01-01'))
    else:
        query = query.limit(50)

    result = query.execute()
    leads = result.data or []

    if not leads:
        print("✅ Sin leads nuevos para notificar.")
        return

    nuevos_admin = 0
    nuevos_tecnico = 0

    for lead in leads:
        lead_id = lead['id']
        nombre = lead.get('nombre_cliente', '?')
        cp = lead.get('codigo_postal', '?')
        ciudad = lead.get('ciudad', '?')
        m2 = lead.get('m2', '?')
        tipo = lead.get('tipo_inmueble', '?')
        telefono = lead.get('telefono_cliente', '?')
        email_cliente = lead.get('email_cliente', '-')
        p_min = lead.get('presupuesto_min', '?')
        p_max = lead.get('presupuesto_max', '?')
        estado = lead.get('estado', '?')
        tecnico = lead.get('tecnicos')  # JOIN result

        # Evitar duplicados por ID
        if last_lead_id and lead_id <= last_lead_id:
            continue

        # Notificar al ADMIN sobre TODO lead nuevo
        if estado == 'nuevo' or (estado == 'asignado' and last_lead_id is None):
            subject_admin = f"🆕 Lead: {nombre} — {m2}m² en {ciudad} ({cp})"
            body_admin = f"""
            <h2>🆕 Nuevo lead en CertificadoYa</h2>
            <table style="border-collapse:collapse;width:100%">
              <tr><td><b>Cliente:</b></td><td>{nombre}</td></tr>
              <tr><td><b>Teléfono:</b></td><td>{telefono}</td></tr>
              <tr><td><b>Email:</b></td><td>{email_cliente}</td></tr>
              <tr><td><b>CP:</b></td><td>{cp} — {ciudad}</td></tr>
              <tr><td><b>m²:</b></td><td>{m2} ({tipo})</td></tr>
              <tr><td><b>Presupuesto:</b></td><td>{p_min}€ – {p_max}€</td></tr>
              <tr><td><b>Estado:</b></td><td>{estado}</td></tr>
            </table>
            <p><a href="https://certificadoya.es">Ver en CertificadoYa</a></p>
            """
            if send_email(ADMIN_EMAIL, subject_admin, body_admin):
                nuevos_admin += 1

        # Notificar al TÉCNICO si está asignado
        if estado == 'asignado' and tecnico:
            t_email = tecnico.get('email', '')
            t_nombre = tecnico.get('nombre', 'Técnico')
            if t_email:
                subject_tecnico = f"📋 Nuevo lead asignado: {m2}m² en {ciudad}"
                body_tecnico = f"""
                <h2>👷 ¡Hola {t_nombre}!</h2>
                <p>Tienes un <b>nuevo lead</b> asignado en CertificadoYa:</p>
                <table style="border-collapse:collapse;width:100%">
                  <tr><td><b>Cliente:</b></td><td>{nombre}</td></tr>
                  <tr><td><b>Teléfono:</b></td><td>{telefono}</td></tr>
                  <tr><td><b>Email:</b></td><td>{email_cliente}</td></tr>
                  <tr><td><b>Dirección:</b></td><td>CP {cp} — {ciudad}</td></tr>
                  <tr><td><b>m²:</b></td><td>{m2} ({tipo})</td></tr>
                  <tr><td><b>Presupuesto estimado:</b></td><td>{p_min}€ – {p_max}€</td></tr>
                </table>
                <p style="margin-top:1rem"><b>Contacta al cliente en menos de 24h</b> para confirmar la visita.</p>
                <p style="color:#666;font-size:.9rem">CertificadoYa — {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                """
                if send_email(t_email, subject_tecnico, body_tecnico):
                    nuevos_tecnico += 1

    # Actualizar estado
    if leads:
        last_lead = leads[-1]
        state['last_lead_id'] = last_lead['id']
        state['last_check_time'] = datetime.now(timezone.utc).isoformat()
        save_state(state)

    print(f"📧 Notificaciones enviadas: {nuevos_admin} al admin, {nuevos_tecnico} a técnicos")


if __name__ == '__main__':
    notify()
