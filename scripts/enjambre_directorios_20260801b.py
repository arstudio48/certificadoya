#!/usr/bin/env python3
"""Enjambre directorios 20260801b — emails CEE nuevos.
Combina: (1) busqueda Brave por ciudad + scrape de webs de despachos,
(2) patrones de dominio {servicio}{ciudad}.es/.com.
Solo stdlib. Excluye historial (.excl_nuevo.json) y ruido.
"""
import json, csv, re, socket, time, random, sys, os
import urllib.request, urllib.parse
from pathlib import Path

BASE = Path.home() / "certificadoya" / "scripts"
OUT_CSV = BASE / "enjambre_directorios_20260801b.csv"
EXCL = BASE / ".excl_nuevo.json"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
socket.setdefaulttimeout(6)

EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")

BAD = ["example", "sentry", "wixpress", "schema.org", "w3.org", "noreply", "no-reply",
       "mailchimp", "cookielaw", "google", "facebook", "twitter", "linkedin", "instagram",
       "pinterest", "youtube", "microsoft", "apple.com", "gob.es", "miteco", "madrid.org",
       "gencat", "xunta", "juntadeandalucia", "coaat", "coam", "cscae", "consejo", "colegio",
       "admon", "secretaria", "prensa", "press", "rrhh", "jobs", "cv@", "info@coaat",
       "@ejemplo", "@dominio", "@tudominio", "test@", "demo@", "tuemail", "yourmail",
       "webmaster", "root@", "admin@", "hostmaster", "soporte", "hacienda", "ayuntamiento",
       "sede@", "registro", "boletin", "hotel", "hoteles", "climiahotels", "climia"]
BAD_TLD = [".png", ".jpg", ".gif", ".css", ".js", ".svg", ".woff", ".webp"]
BAD_DOMAIN = ["certificadosenergeticos.com", "certificadoya.es", "certificadoenergetico.com",
              "guiacertificadoenergetico.com", "certienerg.es", "certigal.com",
              "eseficiencia.es", "eneragen.org", "certificadodeeficienciaenergetica.com",
              "certificadoeficienciaenergeticaespana.com", "certificaplus", "certi-go",
              "tinsa", "endesa", "repsol", "bbva", "idealista", "fotocasa", "habitaclia",
              "miteco.gob.es", "inega", "icaen", "energigas", "endesa", "natury",
              ".fr", ".it", ".pt", ".uk", ".de", ".us", ".mx", ".ar", ".cl", ".co",
              "madrid.org", "gencat.cat", "juntaex", "gva.es", "euskadi", "upm.es",
              "fomento.es", "idae.es"]
OK_END = (".es", ".com", ".net", ".org", ".eus", ".cat", ".gal", ".info")


def clean_email(e):
    e = e.strip().strip(".;,()'\"<>").lower()
    if e.count("@") != 1:
        return None
    if any(b in e for b in BAD):
        return None
    if any(e.endswith(t) for t in BAD_TLD):
        return None
    if not e.endswith(OK_END):
        return None
    for bd in BAD_DOMAIN:
        if bd in e:
            return None
    if not re.match(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", e):
        return None
    dom = e.split("@")[1]
    # permitir gmail personales (despachos pequenos suelen usar gmail), pero filtrar ruido
    if dom in ("hotmail.com", "outlook.com", "yahoo.com"):
        return None
    return e


def fetch(url, timeout=6):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read(300000)
        for enc in ("utf-8", "latin-1"):
            try:
                return data.decode(enc)
            except Exception:
                pass
        return data.decode("utf-8", "ignore")
    except Exception:
        return None


def emails_from_html(html):
    out = set()
    if not html:
        return out
    for e in EMAIL_RE.findall(html):
        c = clean_email(e)
        if c:
            out.add(c)
    return out


def load_exclusions():
    try:
        return set(json.load(open(EXCL, encoding="utf-8")))
    except Exception:
        return set()


def brave_search(query):
    url = "https://search.brave.com/search?q=" + urllib.parse.quote(query)
    html = fetch(url, timeout=8)
    if not html:
        return []
    urls = []
    for m in re.finditer(r'href="(https?://[^"]+)"', html):
        u = m.group(1)
        u = u.replace("&amp;", "&")
        if any(x in u for x in ["brave.com", "google.", "bing.", "facebook.", "twitter.",
                                "youtube.", "wikipedia.org", "reddit.com", "pinterest.",
                                "instagram.", "linkedin."]):
            continue
        # solo dominios .es/.com/.net/.org de despachos (evitar portales grandes)
        if not re.search(r"\.(es|com|net|org|eus|info)(/|$)", u):
            continue
        urls.append(u)
    # dedup por dominio base
    seen = set()
    out = []
    for u in urls:
        base = re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
        if base in seen:
            continue
        seen.add(base)
        out.append(u)
    return out


def slug(city):
    s = city.lower()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
                 ("ñ", "n"), ("ü", "u"), ("ç", "c")]:
        s = s.replace(a, b)
    return s


def main():
    exclusions = load_exclusions()
    print(f"Exclusiones: {len(exclusions)}", flush=True)
    results = {}
    seen = set()

    def record(e, despacho, provincia, nota):
        e = e.lower()
        if e in seen:
            return
        seen.add(e)
        results[e] = (despacho, provincia, nota)

    cities = [
        "Huesca", "Teruel", "Zamora", "Soria", "Ávila", "Segovia", "Palencia",
        "León", "Lugo", "Ourense", "Pontevedra", "Cáceres", "Ciudad Real",
        "Cuenca", "Guadalajara", "Albacete", "Almería", "Jaén", "Huelva",
        "Mérida", "Cartagena", "Lorca", "San Sebastián", "Vitoria", "Logroño",
        "Palma", "Ibiza", "Santa Cruz de Tenerife", "Las Palmas", "Ferrol",
    ]

    # ---- Metodo 1: Brave search por ciudad ----
    print("=== Brave search ===", flush=True)
    for city in cities:
        for q in [f"certificación energética {city} contacto email",
                  f"certificado energético {city} despacho técnico"]:
            urls = brave_search(q)
            time.sleep(1.2)
            for u in urls:
                if any(bd in u for bd in BAD_DOMAIN):
                    continue
                h = fetch(u)
                found = emails_from_html(h)
                if not found:
                    h = fetch(u.rstrip("/") + "/contacto")
                    found = emails_from_html(h)
                if found:
                    for e in found:
                        despacho = re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
                        record(e, despacho, city, "brave")
                time.sleep(random.uniform(0.4, 1.0))
        print(f"  ...{city} done, total {len(results)}", flush=True)

    # ---- Metodo 2: patrones de dominio ----
    print("=== Patrones de dominio ===", flush=True)
    patterns = ["certificadoenergetico{s}", "certificadosenergeticos{s}",
                "certificado-energetico-{s}", "eficienciaenergetica{s}",
                "aparejador{s}", "aparejadores{s}", "arquitectotecnico{s}",
                "certificacionenergetica{s}", "certificado{s}energetico"]
    doms = set()
    for city in cities:
        base = slug(city)
        for s in {base.replace(" ", ""), base.replace(" ", "-")}:
            for pat in patterns:
                for t in (".es", ".com"):
                    doms.add(f"https://{pat.format(s=s)}{t}")
    doms = sorted(doms)
    print(f"Dominios a probar: {len(doms)}", flush=True)
    for idx, dom in enumerate(doms, 1):
        h = fetch(dom)
        found = emails_from_html(h)
        if not found:
            h = fetch(dom + "/contacto")
            found = emails_from_html(h)
        if found:
            low = dom.replace("https://", "").lower()
            base = low.split(".")[0]
            despacho = re.sub(r"certificadoenergetico|certificadosenergeticos|certificado-energetico-"
                              r"|eficienciaenergetica|aparejador|aparejadores|arquitectotecnico"
                              r"|certificacionenergetica", "", base).replace("-", " ").strip()
            provincia = despacho.capitalize() if despacho else "Nacional"
            for e in found:
                record(e, base, provincia, "patron")
            if len([r for r in results.values() if r[2] == "patron"]) <= 3:
                print(f"  [+] {dom} -> {sorted(found)[:2]}", flush=True)
        if idx % 200 == 0:
            print(f"  ...{idx}/{len(doms)}", flush=True)
        time.sleep(random.uniform(0.3, 0.8))

    # ---- Filtrar y guardar ----
    nuevos = {e: (d, p) for e, (d, p, n) in results.items() if e not in exclusions}
    dups = {e for e in results if e in exclusions}
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["email", "despacho", "provincia", "nota"])
        for e in sorted(nuevos):
            d, p = nuevos[e]
            w.writerow([e, d, p, "directorios_20260801b"])

    print("\n===== RESUMEN =====", flush=True)
    print(f"Total emails unicos hallados: {len(results)}", flush=True)
    print(f"  - nuevos: {len(nuevos)}", flush=True)
    print(f"  - duplicados historial: {len(dups)}", flush=True)
    print(f"CSV: {OUT_CSV}", flush=True)
    for e in sorted(nuevos):
        d, p = nuevos[e]
        print(f"  {e} | {d} | {p}", flush=True)


if __name__ == "__main__":
    main()
