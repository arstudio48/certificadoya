#!/usr/bin/env python3
"""Enviar email de invitacion a los prospectos COII Andalucia Occidental (verificados).
Usa Gmail SMTP (funciona en produccion, probado con notify.py).
Solo envia a prospectos de la tabla prospectos_tecnicos que sean COII AOC y no contactados.
"""
import smtplib
import ssl
import re
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from supabase import create_client

# --- Gmail SMTP (funciona en prod) ---
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "arturobriher@gmail.com"
SMTP_PASS = "tlmf yzzq rqmg jcko"
FROM_NAME = "CertificadoYa"
FROM_EMAIL = "arturobriher@gmail.com"
REPLY_TO = "info@certificadoya.es"
WEB = "https://www.certificadoya.es"

# --- Supabase ---
URL = "https://wypgqpgjlookbhuaiyxa.supabase.co"
KEY = "sb_publishable_MsDx5jVGtDAzoB3l3-8DiQ_BxWpChA0"
sb = create_client(URL, KEY)

fecha = datetime.now().strftime("%d/%m/%Y")

def render_html(provincia, colegio, to_email):
    unsub = f"{WEB}/desuscribirse?email={to_email}&source=colegios"
    return f"""<div style="font-family:Outfit,'Segoe UI',system-ui,sans-serif;max-width:600px;margin:0 auto;padding:20px;color:#20201f">
  <div style="border-bottom:2px solid #547c24;padding-bottom:12px;margin-bottom:24px">
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td><h2 style="color:#20201f;margin:0;font-size:22px">Certificado<span style="color:#547c24">Ya</span></h2></td>
        <td align="right" style="font-size:.75rem;color:#8a9973">{fecha}</td>
      </tr>
    </table>
  </div>
  <p style="font-size:15px;line-height:1.5;margin:0 0 12px">Estimados/as,</p>
  <p style="font-size:15px;line-height:1.5;margin:0 0 12px">
    Somos <strong>CertificadoYa</strong> (<a href="{WEB}" style="color:#547c24">certificadoya.es</a>),
    una plataforma que conecta propietarios de viviendas con técnicos certificadores colegiados para el
    Certificado de Eficiencia Energética (CEE).
  </p>
  <p style="font-size:15px;line-height:1.5;margin:0 0 12px">
    En <strong>{provincia}</strong> hay cientos de propietarios buscando técnicos cada mes, y necesitamos
    ampliar nuestra red de profesionales colegiados en la zona.
  </p>
  <div style="background:#f3f9eb;border-radius:10px;padding:20px;margin:20px 0;border:1px solid #e0edcf">
    <p style="font-weight:700;color:#2d3a1f;margin:0 0 10px;font-size:15px">
      ¿Sus colegiados saben que pueden recibir clientes sin invertir en publicidad?
    </p>
    <table width="100%" cellpadding="8" cellspacing="0" border="0" style="font-size:14px"><tr>
      <td style="background:#fff;border-radius:8px;padding:16px;text-align:center;border:1px solid #d4e8c0">
        <span style="font-size:26px;font-weight:700;color:#547c24">18%</span><br>
        <span style="font-size:13px;color:#4a5c3a">de comisión por trabajo</span><br>
        <span style="font-size:11px;color:#7d9470">sin cuota fija · sin permanencia · solo pagas si facturas</span>
      </td>
    </tr></table>
  </div>
  <p style="font-size:15px;line-height:1.5;margin:0 0 12px">
    ¿Podrían <strong>difundir esta oportunidad</strong> entre los colegiados de {colegio}
    a través de su circular, bolsa de trabajo o tablón de anuncios?
  </p>
  <div style="text-align:center;margin:24px 0">
    <a href="{WEB}/panel-tecnicos.html" style="display:inline-block;background:#547c24;color:#fff;text-decoration:none;padding:12px 32px;border-radius:8px;font-weight:600;font-size:15px">Panel de técnicos →</a>
  </div>
  <div style="margin-top:28px;padding-top:16px;border-top:1px solid #eef4e8;font-size:12px;color:#9aab8a">
    <p style="margin:0 0 4px"><strong style="color:#547c24">CertificadoYa</strong> — <a href="{WEB}" style="color:#547c24">certificadoya.es</a></p>
    <p style="margin:0 0 8px"><a href="mailto:info@certificadoya.es" style="color:#547c24">info@certificadoya.es</a> · 641 45 00 68</p>
    <p style="margin:0;font-size:11px;color:#b8c8a9;line-height:1.4">
      Este mensaje se envía a {to_email} como contacto institucional de {colegio}.<br>
      Si no desea recibir más comunicaciones, puede
      <a href="{unsub}" style="color:#547c24;text-decoration:underline">darse de baja aquí</a>.
    </p>
  </div>
</div>"""

def enviar(to_email, provincia, colegio):
    html = render_html(provincia, colegio, to_email)
    texto = re.sub(r"<[^>]+>", "", html)
    subject = f"{provincia} — Oportunidad para colegiados de {colegio} · CertificadoYa"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr((FROM_NAME, FROM_EMAIL))
    msg["To"] = to_email
    msg["Reply-To"] = REPLY_TO
    msg.attach(MIMEText(texto, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls(context=context)
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.sendmail(FROM_EMAIL, [to_email], msg.as_string())
    print(f"  ✅ Enviado a {to_email} ({provincia})")

def main():
    # Leer prospectos COII AOC no contactados
    r = sb.table("prospectos_tecnicos").select("*").eq("contactado", False).execute()
    coii = [p for p in r.data if "coiiaoc.com" in (p.get("email") or "") and not p.get("es_test")]
    print(f"📧 Enviando a {len(coii)} prospectos COII Andalucía Occidental...")
    for p in coii:
        try:
            enviar(p["email"], p["provincia"], p["empresa"])
            # Marcar como contactado (solo campo que existe)
            sb.table("prospectos_tecnicos").update({"contactado": True}).eq("email", p["email"]).execute()
        except Exception as e:
            print(f"  ❌ Error {p['email']}: {e}")
    print("🏁 Hecho.")

if __name__ == "__main__":
    main()
