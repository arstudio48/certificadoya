#!/usr/bin/env bash
# auto_assign.sh — Asignación automática de leads a técnicos + email al técnico con datos del cliente
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

# Obtener credenciales email desde .env (Gmail SMTP usado en auto_assign.py original)
GMAIL_USER=$(grep -E "^SMTP_USER=" .env 2>/dev/null | cut -d= -f2- | tr -d '"' | tr -d "'")
GMAIL_PASS=$(grep -E "^SMTP_PASS=" .env 2>/dev/null | cut -d= -f2- | tr -d '"' | tr -d "'")
ADMIN_EMAIL=$(grep -E "^ADMIN_EMAIL=" .env 2>/dev/null | cut -d= -f2- | tr -d '"' | tr -d "'")
if [ -z "$GMAIL_USER" ]; then GMAIL_USER="Artbriher@gmail.com"; fi
if [ -z "$GMAIL_PASS" ]; then GMAIL_PASS="wmyd dxmf awdezdeo"; fi
if [ -z "$ADMIN_EMAIL" ]; then ADMIN_EMAIL="Artbriher@gmail.com"; fi

# 1. Obtener leads en estado 'nuevo'
LEADS=$(curl -s -H "apikey: $SERVICE_KEY" -H "Authorization: Bearer $SERVICE_KEY" \
  "$SUPABASE_URL/rest/v1/leads?estado=eq.nuevo&select=id,nombre_cliente,provincia,codigo_postal,telefono_cliente,email_cliente,m2,tipo_inmueble,presupuesto_min,notas")

LEAD_COUNT=$(echo "$LEADS" | grep -o '"id"' | wc -l)
echo "Leads nuevos encontrados: $LEAD_COUNT"

if [ "$LEAD_COUNT" -eq 0 ]; then
  echo "No hay leads para asignar. Fin."
  exit 0
fi

echo "$LEADS" | python3 -c "
import sys, json, urllib.request, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SUPABASE_URL = '$SUPABASE_URL'
SERVICE_KEY = '''$SERVICE_KEY'''
GMAIL_USER = '''$GMAIL_USER'''
GMAIL_PASS = '''$GMAIL_PASS'''
ADMIN_EMAIL = '''$ADMIN_EMAIL'''

leads = json.load(sys.stdin)

def get_tecnicos(provincia):
    prov_lower = (provincia or '').lower()
    url = f'{SUPABASE_URL}/rest/v1/tecnicos?select=id,nombre,email,provincia,cp_cobertura,activo,verificado'
    req = urllib.request.Request(url, headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}'})
    try:
        with urllib.request.urlopen(req) as r:
            todos = json.load(r)
        matched = [t for t in todos if t.get('activo') and prov_lower in (t.get('provincia') or '').lower()]
        return matched
    except Exception as e:
        return []

def enviar_email_tecnico(dest, lead):
    nombre = lead.get('nombre_cliente') or 'Cliente'
    tel = lead.get('telefono_cliente') or 'No facilitado'
    email_c = lead.get('email_cliente') or 'No facilitado'
    prov = lead.get('provincia') or '—'
    cp = lead.get('codigo_postal') or '—'
    m2 = lead.get('m2') or '—'
    tipo = lead.get('tipo_inmueble') or '—'
    precio = lead.get('presupuesto_min') or '—'
    notas = lead.get('notas') or ''

    asunto = f'Nuevo encargo CEE — {prov.title()} ({m2} m²)'
    html = f'''
    <div style=\"font-family:Arial,sans-serif;background:#f5f7f2;padding:20px\">
      <div style=\"background:#fff;border-radius:12px;padding:30px;max-width:560px;margin:0 auto\">
        <h1 style=\"color:#16a34a;font-size:22px;margin:0 0 10px\">📋 Nuevo encargo asignado</h1>
        <p style=\"color:#666;line-height:1.6\">Tienes un nuevo certificado energético para gestionar.</p>
        <div style=\"background:#f0faf2;border:1px solid #dce8d0;border-radius:8px;padding:18px;margin:20px 0\">
          <p style=\"color:#1a2e1e;font-weight:bold;margin:0 0 12px\">Datos del cliente:</p>
          <p style=\"color:#6b7b5e;margin:6px 0\"><strong>Nombre:</strong> {nombre}</p>
          <p style=\"color:#6b7b5e;margin:6px 0\"><strong>Teléfono:</strong> <a href=\"tel:{tel}\">{tel}</a></p>
          <p style=\"color:#6b7b5e;margin:6px 0\"><strong>Email:</strong> {email_c}</p>
          <p style=\"color:#6b7b5e;margin:6px 0\"><strong>Provincia:</strong> {prov.title()}</p>
          <p style=\"color:#6b7b5e;margin:6px 0\"><strong>Código postal:</strong> {cp}</p>
          <p style=\"color:#6b7b5e;margin:6px 0\"><strong>Tipo inmueble:</strong> {tipo.title()}</p>
          <p style=\"color:#6b7b5e;margin:6px 0\"><strong>Superficie:</strong> {m2} m²</p>
          <p style=\"color:#6b7b5e;margin:6px 0\"><strong>Presupuesto:</strong> {precio} €</p>
          {f'<p style=\"color:#6b7b5e;margin:6px 0\"><strong>Notas:</strong> {notas}</p>' if notas else ''}
        </div>
        <p style=\"color:#666;line-height:1.6\">Contacta al cliente lo antes posible para fijar la visita. El pago queda retenido hasta la entrega del CEE.</p>
        <p style=\"color:#999;font-size:12px;margin-top:20px\">CertificadoYa — Panel de técnico</p>
      </div>
    </div>
    '''
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = GMAIL_USER
        msg['To'] = dest
        msg['Subject'] = asunto
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        ctx = ssl.create_default_context()
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls(context=ctx)
            s.login(GMAIL_USER, GMAIL_PASS)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f'    ✗ Error enviando email a {dest}: {e}')
        return False

asignados = 0
for lead in leads:
    lid = lead.get('id')
    prov = lead.get('provincia')
    print(f'  Lead {lid[:8]}... provincia={prov}')
    tecnicos = get_tecnicos(prov)
    if tecnicos:
        t = tecnicos[0]
        print(f'    → Asignando a {t[\"nombre\"]} ({t[\"email\"]})')
        update = {'tecnico_asignado': t['id'], 'estado': 'pendiente_tecnico', 'fecha_asignacion': 'now()'}
        url = f'{SUPABASE_URL}/rest/v1/leads?id=eq.{lid}'
        req = urllib.request.Request(url, data=json.dumps(update).encode(),
                                     headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}, method='PATCH')
        try:
            urllib.request.urlopen(req)
            asignados += 1
            print(f'    ✓ Asignado')
            # Enviar email al técnico con datos del cliente
            if enviar_email_tecnico(t['email'], lead):
                print(f'    ✓ Email enviado a técnico')
            else:
                print(f'    ⚠ Email no enviado (error SMTP)')
        except Exception as e:
            print(f'    ✗ Error: {e}')
    else:
        print(f'    ⚠ No hay técnico en {prov} — notificar admin')
        # Notificar al admin que hay lead sin técnico
        try:
            enviar_email_tecnico(ADMIN_EMAIL, lead)
        except:
            pass

print(f'Asignados: {asignados}/{len(leads)}')
"
