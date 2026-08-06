#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ronda 2 de patrones de dominio — provincias con cobertura baja.
Patrones: certificadoenergetico{c}, certificadosenergeticos{c}, certificado-energetico-{c},
aparejador{c}, aparejadores{c}, arquitectotecnico{c}, eficienciaenergetica{c}.
Anti-duplicados contra historial campaña + SMTP + master actual.
"""
import csv, json, re, socket, ssl, time, urllib.request, urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
HIST_CAMPANA = SCRIPT_DIR / ".campana_suscripcion_history.json"
HIST_SMTP = SCRIPT_DIR / ".envio_tecnicos_history.json"
MASTER = SCRIPT_DIR / "tecnicos_campana_20260801_master.csv"

# Provincias con cobertura baja (o sin detectar por dominio)
CIUDADES = [
    # Galicia
    "coruna", "ferrol", "santiago", "vigo", "pontevedra", "ourense", "lugo", "vilagarcia",
    # Norte
    "santander", "gijon", "oviedo", "aviles", "vitoria", "donostia", "san-sebastian", "pamplona",
    # Cataluña / Levante
    "barcelona", "sabadell", "terrassa", "lhospitalet", "tarragona", "reus", "lleida", "girona",
    "castellon", "elche", "torrevieja", "benidorm", "alcoy", "gandia", "sagunto",
    # Centro / Sur
    "guadalajara", "segovia", "soria", "palencia", "zamora", "avila", "ciudadreal", "albacete",
    "huelva", "jaen", "cordoba", "granada", "almeria", "cadiz", "jerez", "malaga", "marbella",
    # Baleares / Canarias
    "ibiza", "menorca", "lanzarote", "fuerteventura", "laspalmas", "tenerife", "la-coruna",
    # Resto
    "huesca", "teruel", "logrono", "badajoz", "caceres", "cartagena", "lorca",
]

PATRONES = [
    "certificadoenergetico{c}", "certificadosenergeticos{c}", "certificado-energetico-{c}",
    "certificadoenergetico{c}.es", "certificadosenergeticos{c}.es",
    "aparejador{c}", "aparejadores{c}", "arquitectotecnico{c}",
    "eficienciaenergetica{c}", "energia{c}",
]

def dominios():
    for c in CIUDADES:
        for p in PATRONES:
            d = p.format(c=c)
            if not d.endswith(('.es', '.com')):
                yield f"{d}.es"
                yield f"{d}.com"
            else:
                yield d

def carga_historiales():
    excl = set()
    for p in (HIST_CAMPANA, HIST_SMTP):
        if p.exists():
            try:
                h = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(h, dict):
                    h = list(h.keys())
                for e in h:
                    if isinstance(e, str) and "@" in e:
                        excl.add(e.lower())
            except Exception:
                pass
    if MASTER.exists():
        with open(MASTER, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("email"):
                    excl.add(r["email"].strip().lower())
    return excl

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
BAD = re.compile(r"(sentry|wixpress|payhip|\.png|\.jpg|\.webp|tudominio|ejemplo|test@|noreply|info@info|@apps|usuario@|tu@email|su@email)", re.I)
ORGANISMO = re.compile(r"@(ayuntamiento|gob\.es|junta|gva\.es|gencat|xunta|aragon\.es|euskadi|madrid\.org|caib\.es|sede|registro)", re.I)
TLD_EXT = re.compile(r"\.(co\.uk|fr|it|pt|de|pe|ar|mx|tech|io|ai)$")

def valido(e):
    if BAD.search(e) or ORGANISMO.search(e) or TLD_EXT.search(e):
        return False
    return True

def fetch(url, timeout=6):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return urllib.request.urlopen(req, timeout=timeout, context=ctx).read().decode("utf-8", errors="ignore")

def main():
    excl = carga_historiales()
    print(f"Exclusiones (anti-duplicado): {len(excl)}")
    nuevos = {}
    total = sum(1 for _ in dominios())
    i = 0
    for dom in dominios():
        i += 1
        if i % 400 == 0:
            print(f"  ...{i}/{total}")
        for base in (f"https://{dom}", f"https://www.{dom}"):
            emails = set()
            ok = False
            for path in ("", "/contacto", "/contactar"):
                url = base + path
                try:
                    html = fetch(url)
                    ok = True
                    emails.update(EMAIL_RE.findall(html))
                    if emails:
                        break
                except Exception:
                    continue
            if not ok:
                break
            for e in emails:
                e = e.lower()
                if e in excl or e in nuevos or not valido(e):
                    continue
                nuevos[e] = dom
            time.sleep(0.4)
            if nuevos:
                break  # ya encontramos emails en este dominio
        time.sleep(0.3)

    print(f"\n=== RESUMEN RONDA 2 ===")
    print(f"Dominios probados: {total} | con emails: {len(nuevos)}")
    out = SCRIPT_DIR / "enjambre_patrones_ronda2_20260801.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["email", "despacho", "provincia", "nota"])
        for e, dom in sorted(nuevos.items()):
            w.writerow([e, dom.replace("www.", ""), "", "patron_ronda2"])
    print(f"Nuevos de esta ronda: {len(nuevos)} -> {out}")
    for e in sorted(nuevos):
        print(f"  {e} | {nuevos[e]}")

if __name__ == "__main__":
    main()
