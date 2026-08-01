"""
campana_suscripcion_tecnicos.py — Envía email corporativo HTML a todos los técnicos
del CSV para que se suscriban a la plataforma CertificadoYa.

- Vía Edge Function enviar-correo (Resend) — Gmail SMTP está en límite diario.
- Botón/baja RGPD discreto al pie: https://www.certificadoya.es/desuscribirse.html?email=...
- Si el técnico hace clic en baja → newsletter-unsubscribe marca activo=false en
  newsletter_subscribers Y activo=false en tecnicos (baja inmediata de la base).
- Historial JSON anti-duplicados + delays anti-spam.
- --dry-run por defecto; --send para envío real (lotes de 20 con pausa).
"""
import os, sys, csv, json, smtplib, time, urllib.request, urllib.error
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Modo SMTP (fallback sin cuota, rotando cuentas Gmail) ---
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
CUENTAS = [
    {"user": "Artbriher@gmail.com", "pass": "wmyd dxmf awdezdeo", "name": "CertificadoYa"},
    {"user": "arturobriher@gmail.com", "pass": "tlmf yzzq rqmg jcko", "name": "CertificadoYa"},
]

def send_one_smtp(row: dict, idx: int) -> dict:
    """Envía por SMTP Gmail directo (sin cuota diaria). Usa el HTML v2 idéntico."""
    html = build_html(row["despacho"], row["provincia"])
    html = html.replace("%EMAIL%", row["email"])
    cuenta = CUENTAS[idx % len(CUENTAS)]
    msg = MIMEMultipart("alternative")
    msg["From"] = f"CertificadoYa <{cuenta['user']}>"
    msg["To"] = row["email"]
    msg["Subject"] = "Clientes para certificados energéticos — 0 € de alta"
    msg.attach(MIMEText(f"Hola, {row['despacho'] or 'colega'}: CertificadoYa conecta propietarios que necesitan su CEE con profesionales como tú. 0€ de alta, 18% comisión, tú eliges tus zonas. Suscríbete en {WEB}/panel-tecnicos.html. Si no quieres recibir más correos: {WEB}/desuscribirse.html?email={row['email']}", "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(cuenta["user"], cuenta["pass"].replace(" ", ""))
            server.sendmail(cuenta["user"], [row["email"]], msg.as_string())
        return {"ok": True, "status": 250, "body": f"SMTP OK ({cuenta['user']})"}
    except Exception as e:
        return {"ok": False, "status": 0, "body": str(e)[:120]}

WEB = "https://www.certificadoya.es"
EDGE = "https://wypgqpgjlookbhuaiyxa.supabase.co/functions/v1/enviar-correo"
CSV_PATH = Path(__file__).parent / "tecnicos_campana_20260801.csv"
if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
    CSV_PATH = Path(sys.argv[1])
HIST = Path(__file__).parent / ".campana_suscripcion_history.json"

PLACEHOLDERS = {
    "sweethome@info.com", "contact@mysite.com",
    "u003ereformas@reformasmallorca.es", "ngar.carlos@gmail.com",
}

def build_html(despacho: str, provincia: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="x-apple-disable-message-reformatting">
  <title>CertificadoYa · Encargos para técnicos</title>
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
    Te enviamos clientes con precio cerrado y pagado. Tú solo certificas. Comisión del 18%.
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
                Encargos de certificado energético, con el cliente ya cerrado
              </p>
              <p style="margin:0 0 16px 0;font-size:15px;line-height:1.6;">
                Hola{', ' + despacho if despacho else ''},
              </p>
              <p style="margin:0 0 16px 0;font-size:15px;line-height:1.6;">
                Somos <strong>CertificadoYa</strong>. Conectamos a propietarios que necesitan un
                CEE con técnicos colegiados de su misma provincia. Estamos ampliando red
                y tu perfil encaja.
              </p>
              <p style="margin:0 0 24px 0;font-size:15px;line-height:1.6;">
                Es sencillo: te enviamos clientes que <strong>ya han reservado y pagado</strong>. Tú haces la visita
                y emites el certificado como siempre. Del cliente, el cobro y el papeleo nos encargamos nosotros.
              </p>
            </td>
          </tr>

          <!-- Beneficios -->
          <tr>
            <td class="px" style="padding:0 40px 8px 40px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f2f8f4;border-radius:12px;">
                <tr>
                  <td style="padding:22px 24px;font-family:Arial,Helvetica,sans-serif;color:#1a2b23;font-size:14px;line-height:1.9;">
                    <strong style="color:#0f6b3d;">✓ Registro gratis</strong> — sin cuotas ni mensualidades.<br>
                    <strong style="color:#0f6b3d;">✓ Comisión del 18%</strong> por encargo — la más baja del sector (la competencia ~30%).<br>
                    <strong style="color:#0f6b3d;">✓ Solo trabajos cerca de ti</strong> — filtrados por provincia y código postal.<br>
                    <strong style="color:#0f6b3d;">✓ Cobro retenido y seguro</strong> — cobras al completar el encargo.
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
                    <span style="font-size:22px;font-weight:bold;color:#0f6b3d;">0€</span><br>
                    <span style="font-size:11px;color:#5c6b63;">Cuota de alta</span>
                  </td>
                  <td align="center" style="font-family:Arial,Helvetica,sans-serif;">
                    <span style="font-size:22px;font-weight:bold;color:#0f6b3d;">18%</span><br>
                    <span style="font-size:11px;color:#5c6b63;">Comisión</span>
                  </td>
                  <td align="center" style="font-family:Arial,Helvetica,sans-serif;">
                    <span style="font-size:22px;font-weight:bold;color:#0f6b3d;">48-96h</span><br>
                    <span style="font-size:11px;color:#5c6b63;">Para estar activo</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CTA -->
          <tr>
            <td class="px btn" align="center" style="padding:28px 40px 8px 40px;">
              <!--[if mso]>
              <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="{WEB}/panel-tecnicos.html" style="height:50px;v-text-anchor:middle;width:280px;" arcsize="20%" fillcolor="#14894f" stroke="f">
              <w:anchorlock/><center style="color:#ffffff;font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">Registrarme gratis →</center>
              </v:roundrect>
              <![endif]-->
              <!--[if !mso]><!-- -->
              <a href="{WEB}/panel-tecnicos.html"
                 style="background-color:#14894f;color:#ffffff;font-family:Arial,Helvetica,sans-serif;font-size:16px;font-weight:bold;padding:15px 34px;border-radius:10px;display:inline-block;">
                 Registrarme gratis →
              </a>
              <!--<![endif]-->
            </td>
          </tr>

          <tr>
            <td class="px" style="padding:12px 40px 34px 40px;font-family:Arial,Helvetica,sans-serif;color:#5c6b63;font-size:13px;line-height:1.6;" align="center">
              El alta lleva 2 minutos. Si prefieres que te lo explique por teléfono, respóndeme y te llamo.
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
                Recibes este correo como profesional del sector de la edificación.
                Si no deseas más comunicaciones, <a href="{WEB}/desuscribirse.html?email=%EMAIL%" style="color:#9fb4a8;text-decoration:underline">date de baja aquí</a> y te retiramos de inmediato.
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>
</body>
</html>"""

def send_one(row: dict) -> dict:
    html = build_html(row["despacho"], row["provincia"])
    html = html.replace("%EMAIL%", row["email"])
    payload = {
        "to": row["email"],
        "subject": "Clientes para certificados energéticos — 0 € de alta",
        "html": html,
        "text": f"Hola, {row['despacho'] or 'colega'}: CertificadoYa conecta propietarios que necesitan su CEE con profesionales como tú. 0€ de alta, 18% comisión, tú eliges tus zonas. Suscríbete en {WEB}/panel-tecnicos.html. Si no quieres recibir más correos: {WEB}/desuscribirse.html?email={row['email']}",
    }
    req = urllib.request.Request(EDGE, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=90)
        return {"ok": True, "status": r.status, "body": r.read().decode()[:200]}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "body": e.read().decode()[:300]}
    except Exception as e:
        return {"ok": False, "status": 0, "body": str(e)}

def main():
    send = "--send" in sys.argv
    use_smtp = "--smtp" in sys.argv
    lotes_de = 20
    pausa_lote = 90
    delay_entre = 3  # segundos entre envíos del mismo lote

    rows = []
    with open(CSV_PATH, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            email = (r.get("email") or "").strip().lower()
            if not email or email in PLACEHOLDERS:
                continue
            if email.count("@") != 1 or "." not in email.split("@")[1]:
                print(f"  [skip] email inválido: {email}")
                continue
            rows.append({"email": email, "provincia": (r.get("provincia") or "").strip(),
                         "despacho": (r.get("despacho") or "").strip()})

    # Deduplicar por email
    seen = set()
    unicos = []
    for r in rows:
        if r["email"] not in seen:
            seen.add(r["email"])
            unicos.append(r)
    rows = unicos

    # Historial
    hist = set()
    if HIST.exists():
        try:
            hist = set(json.loads(HIST.read_text(encoding="utf-8")))
        except Exception:
            hist = set()

    pendientes = [r for r in rows if r["email"] not in hist]
    print(f"Total en CSV (únicos, sin placeholders): {len(rows)}")
    print(f"Ya enviados antes: {len(rows) - len(pendientes)} | Pendientes: {len(pendientes)}")
    if not send:
        print("\n[DRY-RUN] Usa --send para enviar. Primeros 5 destinatarios:")
        for r in pendientes[:5]:
            print(f"  {r['email']:45} {r['provincia']:18} {r['despacho']}")
        return

    ok, fail = 0, 0
    modo = "SMTP" if use_smtp else "Resend"
    print(f"Modo de envío: {modo}")
    # Sin shuffle: el CSV viene ordenado por prioridad (personales P1 primero)
    for i, row in enumerate(pendientes):
        res = send_one_smtp(row, i) if use_smtp else send_one(row)
        if res["ok"]:
            ok += 1
            hist.add(row["email"])
            print(f"  [{i+1}/{len(pendientes)}] OK  {row['email']}  {res['body'][:60]}")
        else:
            fail += 1
            print(f"  [{i+1}/{len(pendientes)}] FAIL {row['email']}  HTTP {res['status']}: {res['body'][:120]}")
        HIST.write_text(json.dumps(sorted(hist)), encoding="utf-8")
        if (i + 1) % lotes_de == 0 and i + 1 < len(pendientes):
            print(f"  --- pausa {pausa_lote}s tras lote {i+1} ---")
            time.sleep(pausa_lote)
        else:
            time.sleep(delay_entre)

    print(f"\nRESULTADO: {ok} enviados, {fail} fallos. Total histórico: {len(hist)}")

if __name__ == "__main__":
    main()
