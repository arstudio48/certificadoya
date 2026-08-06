#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_cluster_cee_2026.py — Scaffolding del cluster SEO "nuevo formato certificado energético 2026".

Genera (o actualiza SOLO los bloques <!--HERMES:INICIO-->/<!--HERMES:FIN--> si existen):
  /guia-cambios-certificado-energetico-2026/            PILAR
  /nuevo-modelo-etiqueta-energetica-2026/               satélite (cliente)
  /formato-xml-certificado-energetico-rd-659-2025/      satélite (técnico)
  /validez-certificado-energetico-antiguo-2026/         satélite (cliente)
  /registro-centralizado-certificado-energetico-2026/   satélite (mixto)
  /certificado-energetico-nuevo-formato-fecha-limite/   satélite (FAQ)

NO publica contenido de cuerpo (<!--CONTENIDO:PENDIENTE-->).
NO despliega. NO ejecuta IndexNow.
"""

import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOY = "2026-07-31"
WEB = "https://www.certificadoya.es"

FECHA_MARKER = "<!--FECHA:CONFIRMAR-BOE-->"

# ---------------------------------------------------------------- datos cluster
# keyword: anchor text de destino
PAGINAS = {
    "guia-cambios-certificado-energetico-2026": {
        "tipo": "pilar",
        "keyword": "cambios certificado energético 2026",
        "title": "Cambios certificado energético 2026: guía completa | CertificadoYa",
        "description": "Guía completa de los cambios del certificado energético en 2026: nuevo formato, etiqueta energética, registro centralizado y validez de los certificados antiguos según el RD 659/2025.",
        "h1": "Cambios del certificado energético en 2026",
        "breadcrumb": "Cambios del certificado energético en 2026",
    },
    "nuevo-modelo-etiqueta-energetica-2026": {
        "tipo": "satelite",
        "keyword": "nuevo modelo de etiqueta energética 2026",
        "title": "Nuevo modelo de etiqueta energética 2026: así será | CertificadoYa",
        "description": "El nuevo modelo de etiqueta energética 2026 cambia letras, colores y escala. Descubre cómo afecta a tu vivienda y qué tienes que hacer para adaptarte.",
        "h1": "Nuevo modelo de etiqueta energética 2026",
        "breadcrumb": "Nuevo modelo de etiqueta energética 2026",
    },
    "formato-xml-certificado-energetico-rd-659-2025": {
        "tipo": "satelite",
        "keyword": "formato XML del certificado energético RD 659/2025",
        "title": "Formato XML certificado energético RD 659/2025: guía técnica | CertificadoYa",
        "description": "Todo sobre el formato XML del certificado energético exigido por el RD 659/2025: estructura, campos obligatorios, generación y validación para técnicos certificadores.",
        "h1": "Formato XML del certificado energético (RD 659/2025)",
        "breadcrumb": "Formato XML del certificado energético (RD 659/2025)",
    },
    "validez-certificado-energetico-antiguo-2026": {
        "tipo": "satelite",
        "keyword": "validez del certificado energético antiguo en 2026",
        "title": "Validez del certificado energético antiguo en 2026 | CertificadoYa",
        "description": "¿Sigue siendo válido tu certificado energético antiguo en 2026? Plazos, caducidad y obligaciones con el nuevo marco normativo. Respuestas claras y directas.",
        "h1": "Validez del certificado energético antiguo en 2026",
        "breadcrumb": "Validez del certificado energético antiguo en 2026",
    },
    "registro-centralizado-certificado-energetico-2026": {
        "tipo": "satelite",
        "keyword": "registro centralizado del certificado energético 2026",
        "title": "Registro centralizado del certificado energético 2026 | CertificadoYa",
        "description": "El registro centralizado del certificado energético 2026 unifica los registros autonómicos. Qué es, cómo funciona y qué implica para propietarios y técnicos.",
        "h1": "Registro centralizado del certificado energético 2026",
        "breadcrumb": "Registro centralizado del certificado energético 2026",
    },
    "certificado-energetico-nuevo-formato-fecha-limite": {
        "tipo": "faq",
        "keyword": "certificado energético nuevo formato fecha límite",
        "title": "Certificado energético nuevo formato: fecha límite y FAQ | CertificadoYa",
        "description": "Fecha límite para el nuevo formato del certificado energético, plazos de adaptación y respuestas a las preguntas más frecuentes sobre el cambio de formato.",
        "h1": "Nuevo formato del certificado energético: fecha límite (FAQ)",
        "breadcrumb": "Nuevo formato del certificado energético: fecha límite (FAQ)",
    },
}

PILAR_SLUG = "guia-cambios-certificado-energetico-2026"
SATELITES = [s for s in PAGINAS if s != PILAR_SLUG]

# ---------------------------------------------------------------- plantilla base
HEADER = """<header class="header">
<div class="header-inner">
<a class="logo" href="/">
<img src="/img/logo-certificadoya-lockup.svg" alt="CertificadoYa" style="height:44px;width:auto">
</a>
<nav class="nav">
<a href="/#como-funciona">Cómo funciona</a>
<a href="/#faq">FAQ</a>
<a href="/blog/">Blog</a>
<a href="/panel-tecnicos.html">¿Eres técnico?</a>
<a class="btn-nav" href="#presupuesto">Presupuesto</a></nav>
<button aria-expanded="false" aria-label="Menú" class="hamburger" id="hamburger-btn">
<span></span><span></span><span></span>
</button>
<!-- Overlay menú móvil -->
<div class="mobile-overlay" id="mobile-overlay">
<div class="mobile-overlay-bg" id="mobile-overlay-bg"></div>
<div class="mobile-overlay-panel" id="mobile-overlay-panel">
<button aria-label="Cerrar menú" class="mobile-overlay-close" id="mobile-overlay-close">✕</button>
<nav class="mobile-overlay-nav">
<a href="/#como-funciona">Cómo funciona</a>
<a href="/#faq">FAQ</a>
<a href="/blog/">Blog</a>
<a href="/panel-tecnicos.html">¿Eres técnico?</a>
<a class="btn-nav" href="#presupuesto" style="margin:0 1rem 1rem;text-align:center">Presupuesto</a>
</nav>
</div>
</div>
</div>
</header>"""

FOOTER = """<footer class="footer-v2">
<div class="footer-grid">
<div class="footer-brand">
<span class="footer-logo">CertificadoYa</span>
<p>Certificados de eficiencia energética (CEE) en toda España. Técnicos colegiados verificados. Presupuesto instantáneo.</p>
</div>
<div class="footer-links">
<strong>Enlaces</strong>
<a href="/blog/">Blog</a>
<a href="/organismos-contacto.html">Organismos oficiales</a>
<a href="/panel-tecnicos.html">¿Eres técnico?</a>
</div>
<div class="footer-links">
<strong>Legal</strong>
<a href="/legal/aviso-legal.html">Aviso legal</a>
<a href="/legal/privacidad.html">Privacidad</a>
<a href="/legal/cookies.html">Cookies</a>
</div>
</div>
<p class="footer-bottom">© 2026 CertificadoYa — ArtStudio</p>
</footer>"""

MENU_JS = """<!-- Menú overlay JS -->
<script>
(function(){
  var btn = document.getElementById('hamburger-btn');
  var overlay = document.getElementById('mobile-overlay');
  var panel = document.getElementById('mobile-overlay-panel');
  var bg = document.getElementById('mobile-overlay-bg');
  var closeBtn = document.getElementById('mobile-overlay-close');
  if (!btn || !overlay) return;
  function openM(){
    overlay.classList.add('open');
    btn.classList.add('active');
    btn.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }
  function closeM(){
    overlay.classList.remove('open');
    btn.classList.remove('active');
    btn.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }
  btn.onclick = function(e){
    e.stopPropagation();
    overlay.classList.contains('open') ? closeM() : openM();
  };
  if (bg) bg.onclick = closeM;
  if (closeBtn) closeBtn.onclick = closeM;
  overlay.querySelectorAll('a').forEach(function(a){
    a.addEventListener('click', closeM);
  });
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && overlay.classList.contains('open')) closeM();
  });
})();
</script>
<script src="/js/chatbot.js" defer></script>
</body>
</html>"""


def json_ld_article(slug, data):
    url = f"{WEB}/{slug}/"
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": data["title"].replace(" | CertificadoYa", ""),
        "description": data["description"],
        "url": url,
        "image": f"{WEB}/img/og-image.png",
        "datePublished": HOY,
        "dateModified": HOY,
        "author": {"@type": "Organization", "name": "CertificadoYa"},
        "publisher": {"@type": "Organization", "name": "CertificadoYa",
                      "logo": {"@type": "ImageObject", "url": f"{WEB}/img/og-image.png"}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }


def json_ld_faq(slug, data):
    url = f"{WEB}/{slug}/"
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question",
             "name": "¿Cuál es la fecha límite para el nuevo formato del certificado energético?",
             "acceptedAnswer": {"@type": "Answer",
                                "text": "La fecha límite definitiva está pendiente de confirmación oficial en el BOE. " + FECHA_MARKER + " Esta página se actualizará en cuanto el calendario sea firme."}},
            {"@type": "Question",
             "name": "¿Qué cambia con el nuevo formato del certificado energético?",
             "acceptedAnswer": {"@type": "Answer",
                                "text": "El nuevo formato introduce el modelo de etiqueta energética revisado y, para certificados nuevos, la generación en XML según el RD 659/2025. La escala de letras, los colores y los campos obligatorios cambian respecto al formato anterior."}},
            {"@type": "Question",
             "name": "¿Tengo que renovar mi certificado energético por el cambio de formato?",
             "acceptedAnswer": {"@type": "Answer",
                                "text": "No necesariamente: mientras tu certificado vigente siga siendo válido, no estás obligado a renovarlo por el mero cambio de formato. Consulta la validez del certificado energético antiguo en 2026 para los plazos exactos."}},
            {"@type": "Question",
             "name": "¿Dónde se registra el certificado con el nuevo formato?",
             "acceptedAnswer": {"@type": "Answer",
                                "text": "Con la entrada en vigor del nuevo marco, los certificados se inscriben en el registro centralizado del certificado energético 2026, que unifica los registros autonómicos."}},
        ],
    }


def json_ld_breadcrumb(slug, data):
    url = f"{WEB}/{slug}/"
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{WEB}/"},
            {"@type": "ListItem", "position": 2, "name": data["breadcrumb"], "item": url},
        ],
    }


def bloque_enlazado(slug):
    """Satélite -> pilar ; pilar -> 5 satélites. Anchor = keyword de destino."""
    if slug == PILAR_SLUG:
        enlaces = "\n".join(
            f'      <li><a href="{WEB}/{s}/">{PAGINAS[s]["keyword"]}</a></li>'
            for s in SATELITES
        )
        html = (
            '<section class="cluster-links">\n'
            "      <h2>Guías relacionadas: el nuevo formato del certificado energético 2026</h2>\n"
            "      <p>Explora el resto de la guía sobre los cambios del certificado energético en 2026:</p>\n"
            "      <ul>\n"
            f"{enlaces}\n"
            "      </ul>\n"
            "    </section>"
        )
    else:
        html = (
            '<section class="cluster-links">\n'
            f'      <p><strong>Artículo principal:</strong> <a href="{WEB}/{PILAR_SLUG}/">{PAGINAS[PILAR_SLUG]["keyword"]}</a></p>\n'
            "    </section>"
        )
    return html


def head_seo(slug, data):
    url = f"{WEB}/{slug}/"
    if data["tipo"] == "faq":
        ld = json.dumps(json_ld_faq(slug, data), ensure_ascii=False, indent=2)
    else:
        ld = json.dumps(json_ld_article(slug, data), ensure_ascii=False, indent=2)
    bc = json.dumps(json_ld_breadcrumb(slug, data), ensure_ascii=False, indent=2)
    return f"""<title>{data["title"]}</title>
    <meta name="description" content="{data["description"]}">
    <link rel="canonical" href="{url}">
    <meta property="og:title" content="{data["title"]}">
    <meta property="og:description" content="{data["description"]}">
    <meta property="og:url" content="{url}">
    <meta property="og:type" content="article">
    <meta property="og:image" content="{WEB}/img/og-image.png">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{data["title"]}">
    <meta name="twitter:description" content="{data["description"]}">
    <script type="application/ld+json">
    {ld}
    </script>
    <script type="application/ld+json">
    {bc}
    </script>"""


def plantilla_completa(slug, data):
    return f"""<!DOCTYPE html>

<html lang="es">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<!--HERMES:INICIO:SEO-->
{head_seo(slug, data)}
<!--HERMES:FIN:SEO-->
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link as="style" href="/css/style.min.css" rel="preload"/>
<link href="/css/style.min.css" rel="stylesheet"/>
<link rel="stylesheet" href="/css/tema-claro-certificadoya.css">
<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/img/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/img/apple-touch-icon-180.png">
<script async="" data-goatcounter="https://certificadoya.goatcounter.com/count" src="//gc.zgo.at/count.js"></script>
</head>
<body>
{HEADER}
<main>
<div class="breadcrumb-v2">
<a href="/">Inicio</a> › {data["breadcrumb"]}
  </div>
<article class="post-single">
<div class="post-header-v2">
<span class="post-cat-v2">guía 2026</span>
<h1>{data["h1"]}</h1>
<p class="blog-date" style="font-size:.8rem;color:#9aab8a;margin-bottom:1rem;">Actualizado: 31 de julio de 2026 · {FECHA_MARKER}</p>
<div class="post-meta-v2">
<span><img alt="Fecha" height="16" src="/img/ico-rapido.svg" style="vertical-align:middle" width="16"/> {HOY}</span>
<span><img alt="Tiempo" height="16" src="/img/ico-rapido.svg" style="vertical-align:middle" width="16"/> Lectura: pendiente</span>
</div>
</div>
<!--HERMES:INICIO:CONTENIDO-->
<div class="post-body">
<!--CONTENIDO:PENDIENTE-->
{bloque_enlazado(slug)}
</div>
<!--HERMES:FIN:CONTENIDO-->
</article>
</main>
{FOOTER}
{MENU_JS}"""


def escribir(slug, data):
    """Idempotente: si el archivo existe, reemplaza SOLO los bloques HERMES."""
    ruta = os.path.join(BASE, slug, "index.html")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    nuevo = plantilla_completa(slug, data)

    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            viejo = f.read()
        # reemplazar bloques SEO
        def reemplazar_bloque(texto, nombre, contenido):
            pat = re.compile(
                rf"<!--HERMES:INICIO:{nombre}-->.*?<!--HERMES:FIN:{nombre}-->",
                re.S,
            )
            if pat.search(texto):
                return pat.sub(
                    f"<!--HERMES:INICIO:{nombre}-->\n{contenido}\n<!--HERMES:FIN:{nombre}-->",
                    texto,
                )
            return texto

        m_seo = re.search(r"<!--HERMES:INICIO:SEO-->.*?<!--HERMES:FIN:SEO-->", nuevo, re.S)
        m_cont = re.search(r"<!--HERMES:INICIO:CONTENIDO-->.*?<!--HERMES:FIN:CONTENIDO-->", nuevo, re.S)
        if m_seo and m_cont:
            viejo = reemplazar_bloque(viejo, "SEO", m_seo.group(0).split("\n", 1)[1].rsplit("\n", 1)[0])
            viejo = reemplazar_bloque(viejo, "CONTENIDO", m_cont.group(0).split("\n", 1)[1].rsplit("\n", 1)[0])
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(viejo)
            print(f"ACTUALIZADO (solo bloques HERMES): {slug}/index.html")
        else:
            print(f"AVISO: {slug}/index.html existe sin bloques HERMES completos. No se toca.")
        return

    with open(ruta, "w", encoding="utf-8") as f:
        f.write(nuevo)
    print(f"CREADO: {slug}/index.html")


def main():
    for slug, data in PAGINAS.items():
        escribir(slug, data)
    print(f"\nCluster generado: {len(PAGINAS)} páginas en {BASE}")


if __name__ == "__main__":
    main()
