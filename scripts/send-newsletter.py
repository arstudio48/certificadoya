#!/usr/bin/env python3
"""
CertificadoYA — Envío masivo de newsletter
Busca suscriptores por tipo en Supabase y envía emails vía Gmail SMTP.
Uso: python3 send-newsletter.py --subject "Título" [--tecnicos "HTML..." --propietarios "..."]
"""
import os, sys, json, argparse, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.request import Request, urlopen
from urllib.error import URLError
from datetime import datetime, timezone

SUPABASE_URL = "https://wypgqpgjlookbhuaiyxa.supabase.co"
SERVICE_KEY = None
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')

# SMTP Gmail
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "Artbriher@gmail.com"
SMTP_PASS = "wmyd dxmf awdezdeo"

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.last_newsletter.json')

def load_env():
    global SERVICE_KEY
    if SERVICE_KEY:
        return
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE):
            if line.startswith('SUPABASE_SERVICE_KEY'):
                SERVICE_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                return
    SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    if not SERVICE_KEY:
        print("ERROR: SUPABASE_SERVICE_KEY no configurada")
        sys.exit(1)

def supabase_get(table, params=""):
    load_env()
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    req = Request(url, headers={
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}"
    })
    with urlopen(req) as r:
        return json.loads(r.read())

def supabase_post(table, data):
    load_env()
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    body = json.dumps(data).encode()
    req = Request(url, data=body, headers={
        "Content-Type": "application/json",
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Prefer": "return=representation"
    })
    with urlopen(req) as r:
        return json.loads(r.read())

def send_email(to, subject, body_html):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"CertificadoYa <{SMTP_USER}>"
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html', 'utf-8'))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"  Error enviando a {to}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Enviar newsletter')
    parser.add_argument('--subject', required=True, help='Asunto del email')
    parser.add_argument('--tecnicos', help='Contenido HTML para técnicos')
    parser.add_argument('--propietarios', help='Contenido HTML para propietarios')
    parser.add_argument('--dry-run', action='store_true', help='No enviar, solo listar')
    parser.add_argument('--limit', type=int, default=0, help='Límite de emails por tipo')
    args = parser.parse_args()

    print(f"\n📬 Newsletter: {args.subject}")
    print(f"{'='*50}")

    if args.tecnicos:
        subs = supabase_get('newsletter_subscribers', 'select=email&user_type=eq.technician&active=eq.true')
        print(f"\n👷 Técnicos: {len(subs)} suscriptores")
        if args.limit:
            subs = subs[:args.limit]
        sent = 0
        for s in subs:
            email = s['email']
            print(f"  {'[DRY-RUN]' if args.dry_run else '[ENVIANDO]'} {email}")
            if not args.dry_run:
                ok = send_email(email, args.subject, args.tecnicos)
                if ok:
                    sent += 1
                    supabase_post('newsletter_subscribers', {
                        'email': email,
                        'last_sent_at': datetime.now(timezone.utc).isoformat()
                    })
        print(f"  → Enviados: {sent}/{len(subs)}")

    if args.propietarios:
        subs = supabase_get('newsletter_subscribers', 'select=email&user_type=eq.owner&active=eq.true')
        print(f"\n🏠 Propietarios: {len(subs)} suscriptores")
        if args.limit:
            subs = subs[:args.limit]
        sent = 0
        for s in subs:
            email = s['email']
            print(f"  {'[DRY-RUN]' if args.dry_run else '[ENVIANDO]'} {email}")
            if not args.dry_run:
                ok = send_email(email, args.subject, args.propietarios)
                if ok:
                    sent += 1
                    supabase_post('newsletter_subscribers', {
                        'email': email,
                        'last_sent_at': datetime.now(timezone.utc).isoformat()
                    })
        print(f"  → Enviados: {sent}/{len(subs)}")

    print(f"\n{'='*50}")
    print("✅ Proceso completado")

if __name__ == '__main__':
    main()
