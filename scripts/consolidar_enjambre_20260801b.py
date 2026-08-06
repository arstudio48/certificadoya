#!/usr/bin/env python3
"""
consolidar_enjambre_20260801b.py — Consolida los CSVs del enjambre de 5 agentes,
cruza contra los historiales anti-duplicados y genera el CSV maestro de pendientes.

Uso: python3 consolidar_enjambre_20260801b.py
"""
import csv, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))

# Historiales anti-duplicados
HIST_CAMPANA = os.path.join(BASE, ".campana_suscripcion_history.json")
HIST_SMTP = os.path.join(BASE, ".envio_tecnicos_history.json")
HIST_SEGUIMIENTO = os.path.join(BASE, ".envio_seguimiento_history.json")

def load_hist(path):
    try:
        d = json.load(open(path))
        if isinstance(d, list):
            return {str(x).lower() for x in d}
        if isinstance(d, dict):
            return {str(k).lower() for k in d.get("enviados", d)}
    except Exception as e:
        print(f"  (historial {path}: {e})")
    return set()

def es_valido(email):
    email = email.strip().lower()
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}$", email):
        return False
    if email.count("@") != 1:
        return False
    # Placeholders / ruido
    if any(x in email for x in ["ejemplo", "example", "tudominio", "test@", "demo@", "noreply", "sentry", "wixpress", "schema.org", "@dominio", "email.com", "your@", "name@", "@gmail.com.com"]):
        return False
    # Organismos
    if any(x in email for x in ["madrid.org", "miteco", "idae.es", "fomento.es", "gva.es", "juntaex", "euskadi", "upm.es", "bzn-", "registrocee", "@012"]):
        return False
    # Buzones institucionales de COLEGIOS (SEDES, no técnicos) — solo si el
    # dominio es institucional (coaat/colegio/ayto/consejo). En dominios
    # privados de despachos, info@/hola@/contacto@ SÍ son válidos.
    dominio = email.split("@")[1] if "@" in email else ""
    local = email.split("@")[0]
    es_sede = any(x in dominio for x in ["coaat", "colegio", ".org", "ayto", "consejo", "caat", "coiic", "coiim", "coii"])
    if es_sede:
        local = email.split("@")[0]
        if re.match(r"^(info|admon|administracion|secretaria|decanosecretario|bibl|borsa|arxiu|visados|pic|gestioneconomica|informatico|buzon|correo|gerencia|presidencia|tesoreria|secretaria_tecnica|webmaster|contacto)($|\.|@)", local):
            return False
    # Grandes estudios / roles (solo dominios corporativos grandes)
    if re.match(r"^(prensa|press|rrhh|jobs|internship|newprojects|cv|communication|development)($|\.|@)", local):
        return False
    # Prefijos numéricos pegados
    if re.match(r"^\d{2,}", local):
        return False
    return True

def main():
    print("=" * 60)
    print("CONSOLIDACIÓN ENJAMBRE 20260801b — CertificadoYa")
    print("=" * 60)

    ya = set()
    for p, nombre in [(HIST_CAMPANA, "campaña"), (HIST_SMTP, "smtp"), (HIST_SEGUIMIENTO, "seguimiento")]:
        h = load_hist(p)
        print(f"  Historial {nombre}: {len(h)}")
        ya |= h
    print(f"  Total ya contactados: {len(ya)}")

    fuentes = [
        "enjambre_colegios_20260801b.csv",
        "enjambre_directorios_20260801b.csv",
        "tecnicos_campana_20260801b.csv",
        "enjambre_social_20260801b.csv",
        "enjambre_foros_20260801b.csv",
        "enjambre_ccaa_20260801b.csv",
    ]

    encontrados = []
    for fn in fuentes:
        path = os.path.join(BASE, fn)
        if not os.path.exists(path):
            print(f"\n  ⚠ No existe: {fn}")
            continue
        rows = list(csv.DictReader(open(path, encoding="utf-8")))
        print(f"\n  {fn}: {len(rows)} filas crudas")
        for r in rows:
            email = (r.get("email") or "").strip().lower()
            if not es_valido(email):
                continue
            if email in ya:
                continue
            encontrados.append({
                "email": email,
                "despacho": (r.get("despacho") or "").strip().title() or "",
                "provincia": (r.get("provincia") or "").strip().title() or "",
                "nota": (r.get("nota") or "").strip() or fn.replace("enjambre_", "").replace("_20260801b.csv", ""),
            })

    # Dedupe final por email
    vistos = set()
    unicos = []
    for r in encontrados:
        if r["email"] not in vistos:
            vistos.add(r["email"])
            unicos.append(r)

    print("\n" + "=" * 60)
    print(f"TOTAL NUEVOS ÚNICOS: {len(unicos)}")
    print("=" * 60)

    if not unicos:
        print("Nada nuevo. No se genera CSV maestro.")
        return

    # Distribución por fuente
    by_src = {}
    for r in unicos:
        by_src[r["nota"]] = by_src.get(r["nota"], 0) + 1
    print("Por fuente:", dict(sorted(by_src.items(), key=lambda x: -x[1])))

    by_prov = {}
    for r in unicos:
        prov = r["provincia"] or "?"
        by_prov[prov] = by_prov.get(prov, 0) + 1
    top_prov = sorted(by_prov.items(), key=lambda x: -x[1])[:8]
    print("Por provincia:", dict(top_prov))

    out = os.path.join(BASE, f"tecnicos_campana_20260801_enjambreB.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["email", "despacho", "provincia", "nota"])
        w.writeheader()
        for r in unicos:
            w.writerow(r)
    print(f"\nCSV maestro: {out}")
    print(f"Primeros 10: {[r['email'] for r in unicos[:10]]}")

if __name__ == "__main__":
    main()
