#!/usr/bin/env python3
"""
envio_seguimiento_leads.py — Seguimiento SMTP a leads asignados sin pago (CertificadoYa).
Reutiliza SMTP Gmail (sin cuota Resend). Filtra leads de prueba. Historial anti-duplicados.
Uso: python3 envio_seguimiento_leads.py           # dry-run
      python3 envio_seguimiento_leads.py --send    # envío real
      python3 envio_seguimiento_leads.py --ejemplo  # envía ejemplo a cuenta de Arturo
"""
import os, sys, csv, json, smtplib, random, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === CONFIG ===
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
# Rotación de cuentas SMTP (Gmail activas; iCloud aparejado@me.com EXPIrada 14/07/2026 — regenerar app password en appleid.apple.com)
CUENTAS = [
    {"user": "Artbriher@gmail.com", "pass": "wmyd dxmf awdezdeo", "name": "CertificadoYa"},
    {"user": "arturobriher@gmail.com", "pass": "tlmf yzzq rqmg jcko", "name": "CertificadoYa"},
]
REPLY_TO = "info@certificadoya.es"
WEB = "https://www.certificadoya.es"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "leads_asignados_seguimiento_20260801.csv")
HISTORY_FILE = os.path.join(BASE_DIR, ".envio_seguimiento_history.json")

# === FILTRO DE LEADS DE PRUEBA ===
TEST_MARKS = ["test", "simulacion", "prop@", "prueba", "60000000", "service key", "test-final", "prod-test"]

def es_test(row):
    blob = " ".join(str(row.get(k, "")) for k in ("nombre_cliente", "email_cliente", "telefono_cliente")).lower()
    return any(m in blob for m in TEST_MARKS)

ASUNTO = "Tu certificado energético en {provincia} — seguimiento de tu solicitud"

EMAIL_HTML = """<!DOCTYPE html>
<html lang="es" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="x-apple-disable-message-reformatting">
  <title>CertificadoYa · Seguimiento de tu solicitud</title>
  <!--[if mso]>
  <style>table,td,div,p,a{{font-family:Arial,Helvetica,sans-serif !important;}}</style>
  <![endif]-->
  <style>
    @media only screen and (max-width:600px){{
      .container{{width:100% !important;}}
      .px{{padding-left:24px !important;padding-right:24px !important;}}
      .btn a{{display:block !important;}}
    }}
    a{{text-decoration:none;}}
  </style>
</head>
<body style="margin:0;padding:0;background-color:#eef2f0;">
  <!-- Preheader (texto de vista previa, oculto) -->
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:#eef2f0;font-size:1px;line-height:1px;">
    Tu solicitud de certificado energético sigue en marcha. Tu técnico asignado te espera.
  </div>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef2f0;">
    <tr>
      <td align="center" style="padding:28px 12px;">

        <table role="presentation" class="container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 6px 24px rgba(16,44,32,0.08);">

          <!-- Cabecera -->
          <tr>
            <td style="background-color:#0f6b3d;background-image:linear-gradient(135deg,#0f6b3d 0%,#14894f 100%);padding:26px 32px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="font-family:Arial,Helvetica,sans-serif;color:#ffffff;font-size:22px;font-weight:bold;letter-spacing:-0.3px;">
                    Certificado<span style="color:#bff0d4;">Ya</span>
                  </td>
                  <td align="right" style="font-family:Arial,Helvetica,sans-serif;color:#bff0d4;font-size:12px;">
                    Certificación energética · España
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Franja A-G energética -->
          <tr>
            <td style="font-size:0;line-height:0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td height="6" style="background-color:#00a651;">&nbsp;</td>
                  <td height="6" style="background-color:#4cb847;">&nbsp;</td>
                  <td height="6" style="background-color:#bfd730;">&nbsp;</td>
                  <td height="6" style="background-color:#fff200;">&nbsp;</td>
                  <td height="6" style="background-color:#fdb913;">&nbsp;</td>
                  <td height="6" style="background-color:#f37021;">&nbsp;</td>
                  <td height="6" style="background-color:#ed1c24;">&nbsp;</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Cuerpo -->
          <tr>
            <td class="px" style="padding:36px 40px 8px 40px;font-family:Arial,Helvetica,sans-serif;color:#1a2b23;">
              <p style="margin:0 0 18px 0;font-size:20px;font-weight:bold;line-height:1.3;color:#0f6b3d;">
                Tu certificado energético, en marcha
              </p>
              <p style="margin:0 0 16px 0;font-size:15px;line-height:1.6;">
                Hola{nombre},
              </p>
              <p style="margin:0 0 16px 0;font-size:15px;line-height:1.6;">
                Te escribimos desde <strong>CertificadoYa</strong> porque solicitaste un
                <strong>certificado de eficiencia energética</strong> para tu vivienda en
                <strong>{provincia}</strong> y queremos asegurarnos de que todo sigue en marcha.
              </p>
              <p style="margin:0 0 24px 0;font-size:15px;line-height:1.6;">
                Tu técnico asignado (<strong>{tecnico}</strong>) está disponible para coordinar
                la visita. El certificado se entrega en <strong>48-96 horas</strong> tras la visita.
              </p>
            </td>
          </tr>

          <!-- Aviso RD 659/2025 -->
          <tr>
            <td class="px" style="padding:0 40px 8px 40px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f2f8f4;border-radius:12px;">
                <tr>
                  <td style="padding:22px 24px;font-family:Arial,Helvetica,sans-serif;color:#1a2b23;font-size:14px;line-height:1.9;">
                    <strong style="color:#0f6b3d;">✓ Obligatorio desde el 23 de julio de 2026</strong> — el certificado energético es
                    imprescindible para vender o alquilar (RD 659/2025), con multas de 300 € a 6.000 €.<br>
                    <strong style="color:#0f6b3d;">✓ ¿Sigues necesitándolo?</strong> Responde a este correo o llama al <strong>{telefono}</strong>
                    y te ponemos en contacto con tu técnico directamente.
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Métricas -->
          <tr>
            <td class="px" style="padding:22px 40px 6px 40px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="font-family:Arial,Helvetica,sans-serif;">
                    <span style="font-size:22px;font-weight:bold;color:#0f6b3d;">48-96h</span><br>
                    <span style="font-size:11px;color:#5c6b63;">Entrega tras la visita</span>
                  </td>
                  <td align="center" style="font-family:Arial,Helvetica,sans-serif;">
                    <span style="font-size:22px;font-weight:bold;color:#0f6b3d;">1 técnico</span><br>
                    <span style="font-size:11px;color:#5c6b63;">Asignado a tu zona</span>
                  </td>
                  <td align="center" style="font-family:Arial,Helvetica,sans-serif;">
                    <span style="font-size:22px;font-weight:bold;color:#0f6b3d;">0 €</span><br>
                    <span style="font-size:11px;color:#5c6b63;">Coste adicional</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CTA -->
          <tr>
            <td class="px btn" align="center" style="padding:28px 40px 8px 40px;">
              <!--[if mso]>
              <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="mailto:info@certificadoya.es" style="height:50px;v-text-anchor:middle;width:280px;" arcsize="20%" fillcolor="#14894f" stroke="f">
              <w:anchorlock/><center style="color:#ffffff;font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">Contactar con mi técnico →</center>
              </v:roundrect>
              <![endif]-->
              <!--[if !mso]><!-- -->
              <a href="mailto:info@certificadoya.es"
                 style="background-color:#14894f;color:#ffffff;font-family:Arial,Helvetica,sans-serif;font-size:16px;font-weight:bold;padding:15px 34px;border-radius:10px;display:inline-block;">
                 Contactar con mi técnico →
              </a>
              <!--<![endif]-->
            </td>
          </tr>

          <tr>
            <td class="px" style="padding:12px 40px 34px 40px;font-family:Arial,Helvetica,sans-serif;color:#5c6b63;font-size:13px;line-height:1.6;" align="center">
              Respondiendo a este correo tu mensaje llega directamente a tu técnico.
            </td>
          </tr>

          <!-- Pie -->
          <tr>
            <td style="background-color:#0f2a1c;padding:26px 40px;font-family:Arial,Helvetica,sans-serif;">
              <p style="margin:0 0 6px 0;color:#ffffff;font-size:14px;font-weight:bold;">CertificadoYa</p>
              <p style="margin:0 0 14px 0;color:#9fb4a8;font-size:12px;line-height:1.6;">
                Certificados de eficiencia energética en toda España.<br>
                📞 641 45 00 68 &nbsp;·&nbsp; ✉️ info@certificadoya.es &nbsp;·&nbsp; certificadoya.es
              </p>
              <p style="margin:0;color:#6b8073;font-size:11px;line-height:1.5;">
                Recibes este correo porque solicitaste tu certificado energético en CertificadoYa.
                Si no deseas más comunicaciones, <a href="{WEB}/desuscribirse.html?email={EMAIL}" style="color:#9fb4a8;text-decoration:underline">date de baja aquí</a> y te retiramos de inmediato.
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>
</body>
</html>"""

EMAIL_TEXT = """Hola{nombre},

Te escribimos desde CertificadoYa porque solicitaste un certificado de eficiencia energética para tu vivienda en {provincia} y queremos asegurarnos de que todo sigue en marcha.

Tu técnico asignado ({tecnico}) está disponible para coordinar la visita. El certificado se entrega en 48-96 horas tras la visita.

¿Sigues necesitando el certificado? Responde a este correo o llama al {telefono} y te ponemos en contacto con tu técnico directamente.

Recuerda: desde el 23 de julio de 2026 el certificado energético es obligatorio para vender o alquilar una vivienda (RD 659/2025), con multas de 300 € a 6.000 €.

Un saludo,
Equipo CertificadoYa
info@certificadoya.es

---
Si no deseas recibir más comunicaciones: {WEB}/desuscribirse.html?email={EMAIL}
"""

def cargar_leads():
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def cargar_historial():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {"enviados": {}, "total_enviados": 0}

def guardar_historial(hist):
    with open(HISTORY_FILE, "w") as f:
        json.dump(hist, f, indent=2, ensure_ascii=False)

def enviar_email(dest, asunto, html, text, cuenta_idx=0):
    cuenta = CUENTAS[cuenta_idx % len(CUENTAS)]
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{cuenta['name']} <{cuenta['user']}>"
        msg["To"] = dest
        msg["Subject"] = asunto
        msg["Reply-To"] = REPLY_TO
        msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(cuenta["user"], cuenta["pass"].replace(" ", ""))
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"  ERROR ({cuenta['user']}): {e}")
        return False

def main():
    dry_run = "--send" not in sys.argv
    modo_ejemplo = "--ejemplo" in sys.argv

    leads = cargar_leads()
    historial = cargar_historial()

    print("=" * 50)
    print("SEGUIMIENTO LEADS ASIGNADOS — CertificadoYa")
    print("=" * 50)
    if dry_run and not modo_ejemplo:
        print("MODO DRY-RUN (no se envía nada) — usa --send")
    else:
        print("MODO ENVÍO REAL")
    print()

    # Filtro: solo leads reales con email
    reales = [r for r in leads if not es_test(r) and r.get("email_cliente", "").strip()]
    tests = [r for r in leads if es_test(r)]
    sin_email = [r for r in leads if not es_test(r) and not r.get("email_cliente", "").strip()]

    print(f"Total leads asignados: {len(leads)}")
    print(f"  - Reales con email (candidatos): {len(reales)}")
    print(f"  - De prueba (filtrados): {len(tests)}")
    print(f"  - Reales sin email (solo SMS): {len(sin_email)}")

    if modo_ejemplo:
        # Envía ejemplo del email a la cuenta de Arturo
        ejemplo = reales[0]
        dest = "arturobriher@gmail.com"
        asunto = ASUNTO.format(provincia=ejemplo["provincia"])
        html = (EMAIL_HTML
                .replace("{nombre}", f" {ejemplo['nombre_cliente'].strip().title()}")
                .replace("{provincia}", ejemplo["provincia"])
                .replace("{tecnico}", ejemplo["tecnico_asignado"].strip().title())
                .replace("{telefono}", ejemplo["telefono_cliente"])
                .replace("{EMAIL}", dest)
                .replace("{WEB}", WEB))
        text = (EMAIL_TEXT
                .replace("{nombre}", f" {ejemplo['nombre_cliente'].strip().title()}")
                .replace("{provincia}", ejemplo["provincia"])
                .replace("{tecnico}", ejemplo["tecnico_asignado"].strip().title())
                .replace("{telefono}", ejemplo["telefono_cliente"])
                .replace("{EMAIL}", dest)
                .replace("{WEB}", WEB))
        print(f"\nEnviando EJEMPLO a {dest} (personalizado como {ejemplo['nombre_cliente'].strip()})...")
        ok = enviar_email(dest, asunto, html, text)
        print(f"  {'OK — revisa tu bandeja' if ok else 'FALLO'}")
        print(f"  Asunto: {asunto}")
        return

    if dry_run:
        print("\n--- DRY-RUN: primeros 5 candidatos ---")
        for r in reales[:5]:
            print(f"  {r['email_cliente']:35s} | {r['provincia']:12s} | {r['dias_sin_contacto']:>3} días | técnico: {r['tecnico_asignado']}")
        print(f"\nTotal candidatos a enviar: {len(reales)}")
        return

    # Envío real: pendientes = reales no enviados antes
    pendientes = [r for r in reales if r["email_cliente"].strip().lower() not in historial["enviados"]]
    print(f"\nPendientes de enviar: {len(pendientes)}")

    if not pendientes:
        print("\nTODOS LOS LEADS REALES YA CONTACTADOS.")
        return

    cuenta_idx = 0
    for i, r in enumerate(pendientes, 1):
        nombre = r["nombre_cliente"].strip().title()
        asunto = ASUNTO.format(provincia=r["provincia"])
        email = r["email_cliente"].strip()
        html = (EMAIL_HTML
                .replace("{nombre}", f" {nombre}")
                .replace("{provincia}", r["provincia"])
                .replace("{tecnico}", r["tecnico_asignado"].strip().title())
                .replace("{telefono}", r["telefono_cliente"])
                .replace("{EMAIL}", email)
                .replace("{WEB}", WEB))
        text = (EMAIL_TEXT
                .replace("{nombre}", f" {nombre}")
                .replace("{provincia}", r["provincia"])
                .replace("{tecnico}", r["tecnico_asignado"].strip().title())
                .replace("{telefono}", r["telefono_cliente"])
                .replace("{EMAIL}", email)
                .replace("{WEB}", WEB))

        print(f"[{i}/{len(pendientes)}] {email:35s} | {r['provincia']:12s} | {r['dias_sin_contacto']:>3} días", end="")
        ok = enviar_email(email, asunto, html, text, cuenta_idx)
        if ok:
            historial["enviados"][email.lower()] = {
                "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
                "provincia": r["provincia"],
                "nombre": nombre,
            }
            historial["total_enviados"] = len(historial["enviados"])
            guardar_historial(historial)
            print("  OK")
            cuenta_idx += 1  # rota cuenta por envío
        else:
            print("  FALLO")
        if i < len(pendientes):
            delay = random.randint(35, 75)
            print(f"  Espera {delay}s...")
            time.sleep(delay)

    print(f"\nEnvío completado: {len(pendientes)} emails.")
    print(f"Total acumulado en historial: {historial['total_enviados']}")

if __name__ == "__main__":
    main()
