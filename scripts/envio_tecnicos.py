#!/usr/bin/env python3
"""
envio_tecnicos.py — Campaña de captación de técnicos CEE para CertificadoYa.
5-15 emails/día, delays aleatorios, historial anti-duplicados, dry-run.
"""
import os, sys, csv, json, smtplib, random, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === CONFIG ===
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "Artbriher@gmail.com"
SMTP_PASS = "wmyd dxmf awdezdeo"
FROM_NAME = "Arturo · CertificadoYa"
FROM_EMAIL = SMTP_USER
REPLY_TO = "info@certificadoya.es"
WEB = "https://www.certificadoya.es"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.expanduser('~/AppData/Local/hermes/scripts/tecnicos_captacion.csv')
HISTORY_FILE = os.path.join(BASE_DIR, '.envio_tecnicos_history.json')
EXCLUSION_FILE = os.path.join(BASE_DIR, 'tecnicos_exclusion.txt')

# === PLANTILLAS DE ASUNTO ===
ASUNTOS = [
    "Encargos de certificados energéticos en {zona} — sin buscar clientes",
    "¿Te interesan leads de CEE en {zona}?",
    "Clientes para certificados energéticos en {zona} — 0€ de alta",
    "CertificadoYa: encargos de CEE en {zona} con pago garantizado",
]

# === PLANTILLA DE EMAIL ===
EMAIL_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:0 auto;padding:20px">
  <p>Hola,</p>
  <p>Me pongo en contacto contigo porque trabajáis con certificados de eficiencia energética y quizá os encaje lo que hacemos en <b>CertificadoYa</b>.</p>
  <p>Conectamos a propietarios que necesitan un CEE con técnicos certificadores de su provincia. Tú recibes el encargo con el <b>precio ya cerrado y el cliente filtrado por zona</b> — solo tienes que aceptar, hacer la visita y registrar el certificado.</p>
  <p><b>Por qué puede interesarte:</b></p>
  <ul>
    <li><b>0 € de alta</b> y sin cuota mensual (otras plataformas cobran 15-30 €/mes)</li>
    <li><b>Comisión del 18%</b> — la más baja del sector (la competencia está en 25-30%)</li>
    <li><b>Pago garantizado</b>: el dinero queda retenido y se te abona al registrar el CEE</li>
    <li>Eliges solo los encargos de tu zona que te interesen</li>
  </ul>
  <p>Ya hemos gestionado <b>+1.200 certificados</b> con técnicos de toda España.</p>
  <p>Si quieres echar un vistazo a los encargos disponibles en tu provincia, el registro es gratuito: <a href="{WEB}/tecnicos">{WEB}/tecnicos</a></p>
  <p>Un saludo,<br><b>Arturo</b><br>CertificadoYa · <a href="mailto:info@certificadoya.es">info@certificadoya.es</a> · 641 45 00 68</p>
  <hr style="border:none;border-top:1px solid #eee;margin-top:30px">
  <p style="font-size:11px;color:#999">Si no deseas recibir más comunicaciones, <a href="{WEB}/desuscribirse?email={EMAIL}&source=tecnicos">darte de baja aquí</a>.</p>
</body>
</html>"""

EMAIL_TEXT = """Hola,

Me pongo en contacto contigo porque trabajáis con certificados de eficiencia energética y quizá os encaje lo que hacemos en CertificadoYa.

Conectamos a propietarios que necesitan un CEE con técnicos certificadores de su provincia. Tú recibes el encargo con el precio ya cerrado y el cliente filtrado por zona — solo tienes que aceptar, hacer la visita y registrar el certificado.

Por qué puede interesarte:
- 0 € de alta y sin cuota mensual (otras plataformas cobran 15-30 €/mes)
- Comisión del 18% — la más baja del sector (la competencia está en 25-30%)
- Pago garantizado: el dinero queda retenido y se te abona al registrar el CEE
- Eliges solo los encargos de tu zona que te interesen

Ya hemos gestionado +1.200 certificados con técnicos de toda España.

Si quieres echar un vistazo a los encargos disponibles en tu provincia, el registro es gratuito: {WEB}/tecnicos

Un saludo,
Arturo
CertificadoYa · info@certificadoya.es · 641 45 00 68

---
Si no deseas recibir más comunicaciones: {WEB}/desuscribirse?email={EMAIL}&source=tecnicos
"""

def cargar_csv():
    """Lee el CSV de técnicos"""
    tecnicos = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            email = row.get('email', '').strip().lower()
            if email:
                tecnicos.append({
                    'email': email,
                    'provincia': row.get('provincia', '').strip(),
                    'dominio': row.get('dominio', '').strip(),
                    'tipo': row.get('tipo', 'personal'),
                })
    return tecnicos

def cargar_historial():
    """Carga historial de envíos"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {'enviados': {}, 'fecha_ultimo': None, 'total_enviados': 0}

def guardar_historial(hist):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(hist, f, indent=2)

def cargar_exclusiones():
    excl = set()
    if os.path.exists(EXCLUSION_FILE):
        with open(EXCLUSION_FILE) as f:
            for line in f:
                e = line.strip().lower()
                if e: excl.add(e)
    return excl

def enviar_email(dest, asunto, html, text):
    """Envía email vía SMTP Gmail"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = dest
        msg['Subject'] = asunto
        msg['Reply-To'] = REPLY_TO
        msg.attach(MIMEText(text, 'plain', 'utf-8'))
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    dry_run = '--send' not in sys.argv
    
    print(f"{'='*50}")
    print(f"📧 CAMPAÑA CAPTACIÓN TÉCNICOS CEE")
    print(f"{'='*50}")
    if dry_run:
        print(f"🔴 MODO DRY-RUN (no se enviará nada)")
        print(f"   Añade --send para enviar de verdad")
    else:
        print(f"🟢 MODO ENVÍO REAL")
    print()
    
    # Cargar datos
    tecnicos = cargar_csv()
    historial = cargar_historial()
    exclusiones = cargar_exclusiones()
    
    print(f"Técnicos en CSV: {len(tecnicos)}")
    print(f"Ya enviados: {len(historial['enviados'])}")
    print(f"Excluidos (bajas): {len(exclusiones)}")
    
    # Pendientes
    pendientes = []
    for t in tecnicos:
        email = t['email']
        if email in historial['enviados']:
            continue
        if email in exclusiones:
            continue
        pendientes.append(t)
    
    if not pendientes:
        print("\n✅ LISTA COMPLETADA — no quedan técnicos por contactar.")
        return
    
    print(f"Pendientes de enviar: {len(pendientes)}")
    
    # Seleccionar lote (5-15 aleatorio)
    random.shuffle(pendientes)
    lote_size = random.randint(5, 15)
    lote = pendientes[:lote_size]
    
    print(f"\nLote de hoy: {len(lote)} emails")
    print()
    
    for i, t in enumerate(lote, 1):
        provincia = t['provincia'] or 'tu zona'
        asunto = random.choice(ASUNTOS).format(zona=provincia)
        
        html = EMAIL_HTML.replace('{WEB}', WEB).replace('{EMAIL}', t['email'])
        text = EMAIL_TEXT.replace('{WEB}', WEB).replace('{EMAIL}', t['email'])
        
        print(f"[{i}/{len(lote)}] {t['email']:45s} | {provincia:20s}", end='')
        
        if dry_run:
            print(f" | Asunto: {asunto}")
            print(f"     ✅ (dry-run)")
        else:
            print(f" | Asunto: {asunto[:40]}...")
            ok = enviar_email(t['email'], asunto, html, text)
            if ok:
                historial['enviados'][t['email']] = {
                    'fecha': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'provincia': provincia,
                    'dominio': t['dominio'],
                    'tipo': t['tipo'],
                }
                historial['total_enviados'] = len(historial['enviados'])
                historial['fecha_ultimo'] = time.strftime('%Y-%m-%d %H:%M:%S')
                guardar_historial(historial)
                print(f"     ✅ Enviado")
            else:
                print(f"     ❌ Fallo")
        
        # Delay entre envíos (solo en modo real)
        if not dry_run and i < len(lote):
            delay = random.randint(40, 90)
            print(f"     ⏱ Espera {delay}s...")
            time.sleep(delay)
    
    # Resumen
    print(f"\n{'='*50}")
    if dry_run:
        print(f"🔴 DRY-RUN completado — {len(lote)} emails simulados")
        print(f"   Ejecuta con --send para enviar realmente")
    else:
        print(f"🟢 Envío completado: {len(lote)} emails")
        print(f"   Total acumulado: {historial['total_enviados']}/{len(tecnicos)}")
    
    if historial['total_enviados'] >= len(tecnicos):
        print(f"\n✅ LISTA COMPLETADA — todos los técnicos han sido contactados.")

if __name__ == '__main__':
    main()
