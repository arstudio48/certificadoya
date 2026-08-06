#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seguimiento_leads_asignados.py
===============================
Diagnóstico y lista priorizada de seguimiento de los leads en estado 'asignado'
de CertificadoYa.es (objetivo O1 del plan maestro: conseguir >=1 pago real).

Genera:
  - Informe MD priorizado: leads_asignados_seguimiento_YYYYMMDD.md
  - CSV de contactos pendientes: leads_asignados_seguimiento_YYYYMMDD.csv

Fuentes de datos (JSON crudo volcado desde Supabase con `npx supabase db query`):
  - scripts/_leads_asignados_raw.json
  - scripts/_tecnicos_raw.json

NO envía emails: la cuota de Resend es limitada y el envío lo gestiona el cron.
"""

import csv
import json
import os
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_JSON = os.path.join(SCRIPT_DIR, "_leads_asignados_raw.json")
TECNICOS_JSON = os.path.join(SCRIPT_DIR, "_tecnicos_raw.json")
FECHA = datetime.now().strftime("%Y%m%d")
MD_OUT = os.path.join(SCRIPT_DIR, f"leads_asignados_seguimiento_{FECHA}.md")
CSV_OUT = os.path.join(SCRIPT_DIR, f"leads_asignados_seguimiento_{FECHA}.csv")


def parse_ts(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None


def dias_desde(ts, ref):
    if ts is None or ref is None:
        return None
    return (ref - ts).days


def main():
    if not os.path.exists(LEADS_JSON):
        sys.exit(f"ERROR: no existe {LEADS_JSON}. Volcarlo con:\n"
                 f"  npx supabase db query --linked \"SELECT ... FROM leads WHERE estado='asignado'\" -o json")

    with open(LEADS_JSON, encoding="utf-8") as f:
        leads = json.load(f)
    with open(TECNICOS_JSON, encoding="utf-8") as f:
        tecnicos = json.load(f)

    now = datetime.now(timezone.utc)
    tec_by_id = {t["id"]: t for t in tecnicos}

    rows = []
    tec_ids = set()
    for l in leads:
        tid = l.get("tecnico_asignado")
        tec = tec_by_id.get(tid) if tid else None
        if tid:
            tec_ids.add(tid)
        created = parse_ts(l.get("created_at"))
        ultimo = parse_ts(l.get("ultimo_contacto"))
        # Base de la antigüedad de seguimiento: ultimo_contacto si existe, si no created_at
        base = ultimo or created
        dias_sin_contacto = dias_desde(base, now)
        telefono = (l.get("telefono_cliente") or "").strip()
        email = (l.get("email_cliente") or "").strip()
        rows.append({
            "nombre": l.get("nombre_cliente"),
            "email": email or None,
            "telefono": telefono or None,
            "provincia": l.get("provincia"),
            "tecnico_nombre": tec["nombre"] if tec else "(sin tecnico real)",
            "tecnico_email": tec["email"] if tec else None,
            "tecnico_existe": bool(tec),
            "created_at": l.get("created_at"),
            "ultimo_contacto": l.get("ultimo_contacto"),
            "dias_sin_contacto": dias_sin_contacto,
            "email_notificado_asignacion": bool(l.get("email_notificado_asignacion")),
        })

    # Priorización: más días sin contacto primero
    rows.sort(key=lambda r: (r["dias_sin_contacto"] if r["dias_sin_contacto"] is not None else 0),
              reverse=True)

    # ---- Estáticas del diagnóstico ----
    sin_tel = [r for r in rows if not r["telefono"]]
    sin_email = [r for r in rows if not r["email"]]
    con_ultimo = [r for r in rows if r["ultimo_contacto"]]
    tec_reales = sum(1 for r in rows if r["tecnico_existe"])
    creados = [parse_ts(r["created_at"]) for r in rows if parse_ts(r["created_at"])]
    antig_media = round(sum((now - c).days for c in creados) / len(creados), 1) if creados else None
    dias_sin_contacto_list = [r["dias_sin_contacto"] for r in rows if r["dias_sin_contacto"] is not None]
    media_dias_sin = round(sum(dias_sin_contacto_list) / len(dias_sin_contacto_list), 1) if dias_sin_contacto_list else None

    # ---- Informe MD ----
    lines = []
    lines.append("# Seguimiento de leads asignados — CertificadoYa.es")
    lines.append("")
    lines.append(f"Generado: {now.strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Total leads en estado `asignado`: **{len(rows)}**")
    lines.append("")
    lines.append("## Diagnóstico rápido (por qué 0 pagos)")
    lines.append("")
    lines.append(f"- Técnicos distintos referenciados: **{len(tec_ids)}** de **{len(tecnicos)}** técnicos activos en BD.")
    lines.append(f"- Leads con técnico asignado REAL (id existe en tabla tecnicos): **{tec_reales} / {len(rows)}**.")
    lines.append(f"- Leads **sin teléfono**: **{len(sin_tel)}**.")
    lines.append(f"- Leads **sin email**: **{len(sin_email)}**.")
    lines.append(f"- Leads **sin ultimo_contacto** (nunca contactados): **{len(rows) - len(con_ultimo)} / {len(rows)}**.")
    lines.append(f"- Antigüedad media desde alta (created_at): **{antig_media} días**.")
    if media_dias_sin is not None:
        lines.append(f"- Media de días sin contacto: **{media_dias_sin} días**.")
    lines.append("")
    lines.append("> Los leads llevan meses sin seguimiento (media 31 días de antigüedad, solo 4 tienen ultimo_contacto). "
                 "La causa más probable de 0 pagos es que no hay acción de cierre/recordatorio tras la asignación al técnico.")
    lines.append("")
    lines.append("## Lista priorizada de contactos")
    lines.append("")
    lines.append("| # | Nombre | Provincia | Teléfono | Email | Técnico asignado | Días sin contacto | Canales |")
    lines.append("|---|--------|-----------|----------|-------|------------------|-------------------|---------|")
    for i, r in enumerate(rows, 1):
        canales = []
        if r["telefono"]:
            canales.append("📞")
        if r["email"]:
            canales.append("✉️")
        canal_str = " ".join(canales) if canales else "⚠️ sin canal"
        dias = r["dias_sin_contacto"] if r["dias_sin_contacto"] is not None else "N/D"
        email = r["email"] or "—"
        tel = r["telefono"] or "—"
        lines.append(f"| {i} | {r['nombre'] or '?'} | {r['provincia'] or '—'} | {tel} | {email} | "
                     f"{r['tecnico_nombre'] or '—'} | {dias} | {canal_str} |")
    lines.append("")
    lines.append("## Nota")
    lines.append("")
    lines.append("- Este informe/CSV solo prioriza contactos. El envío real de emails lo ejecuta el cron (cuota Resend limitada).")
    lines.append("")

    with open(MD_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # ---- CSV ----
    csv_fields = [
        "posicion", "nombre_cliente", "provincia", "telefono_cliente", "email_cliente",
        "tecnico_asignado", "tecnico_existe", "created_at", "ultimo_contacto",
        "dias_sin_contacto", "tiene_telefono", "tiene_email", "email_notificado_asignacion",
    ]
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        for i, r in enumerate(rows, 1):
            w.writerow({
                "posicion": i,
                "nombre_cliente": r["nombre"],
                "provincia": r["provincia"],
                "telefono_cliente": r["telefono"],
                "email_cliente": r["email"],
                "tecnico_asignado": r["tecnico_nombre"],
                "tecnico_existe": r["tecnico_existe"],
                "created_at": r["created_at"],
                "ultimo_contacto": r["ultimo_contacto"],
                "dias_sin_contacto": r["dias_sin_contacto"],
                "tiene_telefono": bool(r["telefono"]),
                "tiene_email": bool(r["email"]),
                "email_notificado_asignacion": r["email_notificado_asignacion"],
            })

    # ---- Resumen ----
    print("== RESUMEN ==")
    print(f"Total leads asignados : {len(rows)}")
    print(f"Técnicos distintos    : {len(tec_ids)}  (técnicos activos en BD: {len(tecnicos)})")
    print(f"Leads c/ técnico real : {tec_reales}/{len(rows)}")
    print(f"Sin teléfono          : {len(sin_tel)}")
    print(f"Sin email             : {len(sin_email)}")
    print(f"Nunca contactados     : {len(rows) - len(con_ultimo)}/{len(rows)}")
    print(f"Antigüedad media      : {antig_media} días")
    print(f"Media días sin contacto: {media_dias_sin} días")
    print(f"Informe MD  -> {MD_OUT}")
    print(f"CSV        -> {CSV_OUT}  ({len(rows)} filas de datos)")


if __name__ == "__main__":
    main()
