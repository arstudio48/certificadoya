#!/usr/bin/env python3
"""Añade menú hamburguesa móvil a páginas de CertificadoYa que no lo tienen."""

CSS_HAMBURGUESA = """
    .hamburger{display:none;flex-direction:column;justify-content:center;align-items:center;width:36px;height:36px;background:none;border:none;cursor:pointer;gap:5px;padding:4px;z-index:200;position:relative}
    .hamburger span{display:block;width:22px;height:2.5px;background:#333;border-radius:2px;transition:transform .25s ease,opacity .25s ease}
    .hamburger.active span:nth-child(1){transform:translateY(7.5px) rotate(45deg)}
    .hamburger.active span:nth-child(2){opacity:0}
    .hamburger.active span:nth-child(3){transform:translateY(-7.5px) rotate(-45deg)}
    .mobile-menu{display:none;position:absolute;top:64px;left:0;right:0;background:#fff;border-bottom:1px solid #e5e7eb;box-shadow:0 4px 12px rgba(0,0,0,.08);z-index:99;flex-direction:column}
    .mobile-menu.open{display:flex}
    .mobile-menu a{padding:.8rem 1.2rem;font-size:.95rem;font-weight:500;color:#20201f;text-decoration:none;border-bottom:1px solid #f0f0f0;transition:background .15s}
    .mobile-menu a:hover{background:#f3f9eb;color:#547c24}
    .mobile-menu .btn-nav{margin:.5rem 1rem}
    @media(max-width:600px){.hamburger{display:flex}.nav>a,.nav>.buscador-wrapper,.nav>.btn-nav{display:none}.header-inner{position:relative}}
"""

HAMBURGUESA_BTN = """      <button class="hamburger" id="hamburger-btn" aria-label="Menú" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>"""

MOBILE_MENU = """    <div class="mobile-menu" id="mobile-menu">
      <a href="/#como-funciona">C\u00f3mo funciona</a>
      <a href="/#faq">Preguntas frecuentes</a>
      <a href="/blog/">Blog</a>
      <a href="/inmobiliarias.html">Inmobiliarias</a>
      <strong style="display:block;padding:.6rem 1.2rem;font-size:.82rem;color:#9aab8a;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #f0f0f0">T\u00e9cnicos</strong>
      <a href="/panel-tecnicos.html">Registro de t\u00e9cnicos</a>
      <a href="/pool-encargos.html">Trabajos</a>
      <a href="/blog/?cat=tecnicos">Blog t\u00e9cnico</a>
      <a href="/tecnicos/">Directorio de t\u00e9cnicos</a>
      <a href="#presupuesto-card" class="btn-nav" style="margin:0 1rem 1rem;text-align:center">Presupuesto</a>
    </div>"""

MOBILE_MENU_SIMPLE = """    <div class="mobile-menu" id="mobile-menu">
      <a href="/#como-funciona">C\u00f3mo funciona</a>
      <a href="/#faq">Preguntas frecuentes</a>
      <a href="/blog/">Blog</a>
      <a href="/inmobiliarias.html">Inmobiliarias</a>
      <strong style="display:block;padding:.6rem 1.2rem;font-size:.82rem;color:#9aab8a;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #f0f0f0">T\u00e9cnicos</strong>
      <a href="/panel-tecnicos.html">Registro de t\u00e9cnicos</a>
      <a href="/pool-encargos.html">Trabajos</a>
      <a href="/blog/?cat=tecnicos">Blog t\u00e9cnico</a>
      <a href="/tecnicos/">Directorio de t\u00e9cnicos</a>
      <a href="/#presupuesto-card" class="btn-nav" style="margin:0 1rem 1rem;text-align:center">Presupuesto</a>
    </div>"""

JS_HAMBURGUESA = """<script>
document.addEventListener('DOMContentLoaded',function(){var b=document.getElementById('hamburger-btn'),m=document.getElementById('mobile-menu');if(b&&m){b.addEventListener('click',function(){var e=this.getAttribute('aria-expanded')==='true'?false:true;this.setAttribute('aria-expanded',e);this.classList.toggle('active');m.classList.toggle('open')})}});
</script>"""


def add_css_if_missing(content, css_block):
    """Añade CSS de hamburguesa al bloque <style> si no existe."""
    if '.hamburger{' in content:
        return content, False
    # Insertar justo antes de </style>
    idx = content.rfind('</style>')
    if idx == -1:
        return content, False
    content = content[:idx] + css_block + content[idx:]
    return content, True


def add_js_if_missing(content):
    """Añade JS de hamburguesa antes de </body> si no existe."""
    if 'hamburger-btn' in content and 'addEventListener' in content:
        return content, False
    if 'hamburger-btn' not in content:
        return content, False
    idx = content.rfind('</body>')
    if idx == -1:
        return content, False
    content = content[:idx] + '  ' + JS_HAMBURGUESA + '\n' + content[idx:]
    return content, True


def add_btn_in_nav(content):
    """Añade botón hamburguesa dentro del <nav> si no existe."""
    if 'hamburger-btn' in content:
        return content, False
    idx = content.find('</nav>')
    if idx == -1:
        return content, False
    content = content[:idx] + '  ' + HAMBURGUESA_BTN + '\n' + content[idx:]
    return content, True


def add_menu_after_nav(content):
    """Añade menú móvil después de </nav> si no existe."""
    if 'mobile-menu' in content and 'Técnicos' in content:
        return content, False
    nav_close = content.find('</nav>')
    if nav_close == -1:
        return content, False
    # Buscar la línea después de </nav>
    after_nav = content[nav_close:]
    # Insertar el menú justo después de </nav>
    content = content[:nav_close+6] + '\n' + MOBILE_MENU + '\n' + content[nav_close+6:]
    return content, True


def enrich_mobile_menu(content):
    """Enriquece el menú móvil existente añadiendo Trabajos, Inmobiliarias, Técnicos si faltan."""
    if 'Trabajos' in content and 'Inmobiliarias' in content and 'Técnicos' in content:
        return content, False
    
    # Encontrar el bloque mobile-menu
    start = content.find('<div class="mobile-menu"')
    if start == -1:
        return content, False
    end = content.find('</div>', start)
    end = content.find('</div>', end)  # segundo cierre porque hay un div anidado? No, es la lista de links
    # Mejor buscar el cierre correcto del mobile-menu
    end = content.find('</div>', content.find('id="mobile-menu"'))
    if end == -1:
        return content, False
    
    old_menu = content[start:end+6]
    
    has_tecnicos = 'Técnicos' in old_menu or 'técnicos' in old_menu.lower()
    has_trabajos = 'Trabajos' in old_menu or 'Trabajos' in old_menu or 'pool-encargos' in old_menu
    has_inmobiliarias = 'Inmobiliarias' in old_menu or 'inmobiliarias' in old_menu
    has_blog = 'Blog' in old_menu
    has_presupuesto = 'Presupuesto' in old_menu or 'presupuesto' in old_menu
    
    # Build new menu content
    links = []
    
    # If page already has full menu, skip
    if has_blog and has_trabajos and has_inmobiliarias and has_tecnicos:
        return content, False
    
    # Parse existing links
    import re
    existing_links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>', old_menu)
    existing_hrefs = [h for h, _ in existing_links]
    existing_texts = [t.strip() for _, t in existing_links]
    
    # Build complete menu
    menu_items = []
    
    # 1. Cómo funciona
    if not any('como-funciona' in h for h in existing_hrefs) and not any('Cómo funciona' in t for t in existing_texts):
        if not any('#como-funciona' in h or 'como-funciona' in h for h in existing_hrefs):
            menu_items.append(('C\u00f3mo funciona', '/#como-funciona'))
    
    # 2. FAQ
    if not any('#faq' in h or 'faq' in h for h in existing_hrefs) and not any('FAQ' in t for t in existing_texts):
        menu_items.append(('Preguntas frecuentes', '/#faq'))
    
    # 3. Blog
    if not has_blog:
        menu_items.append(('Blog', '/blog/'))
    
    # 4. Inmobiliarias
    if not has_inmobiliarias:
        menu_items.append(('Inmobiliarias', '/inmobiliarias.html'))
    
    # 5. Técnicos header
    # 6. Registro de técnicos
    # 7. Trabajos  
    # 8. Blog técnico
    # 9. Directorio
    menu_items.append(('__TECNICOS_HEADER__', ''))
    menu_items.append(('Registro de t\u00e9cnicos', '/panel-tecnicos.html'))
    menu_items.append(('Trabajos', '/pool-encargos.html'))
    menu_items.append(('Blog t\u00e9cnico', '/blog/?cat=tecnicos'))
    menu_items.append(('Directorio de t\u00e9cnicos', '/tecnicos/'))
    
    # 10. Presupuesto
    menu_items.append(('__PRESUPUESTO__', ''))
    
    # Build new menu HTML
    new_menu = '    <div class="mobile-menu" id="mobile-menu">\n'
    for text, href in menu_items:
        if text == '__TECNICOS_HEADER__':
            new_menu += '      <strong style="display:block;padding:.6rem 1.2rem;font-size:.82rem;color:#9aab8a;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #f0f0f0">T\u00e9cnicos</strong>\n'
        elif text == '__PRESUPUESTO__':
            new_menu += '      <a href="/#presupuesto-card" class="btn-nav" style="margin:0 1rem 1rem;text-align:center">Presupuesto</a>\n'
        else:
            new_menu += f'      <a href="{href}">{text}</a>\n'
    new_menu += '    </div>'
    
    content = content[:start] + new_menu + content[end+6:]
    return content, True


def process_pool_encargos(content):
    """Pool-encargos tiene .header-pool en vez de <header class='header'> con nav."""
    if 'hamburger-btn' in content:
        return content, False
    changes = False
    
    # Add CSS
    content, c = add_css_if_missing(content, CSS_HAMBURGUESA)
    changes = changes or c
    
    # Add hamburger button & mobile menu inside .header-pool div, after .user-info
    # Find user-info div
    ui_end = content.find('</div>', content.find('user-info'))
    if ui_end == -1:
        ui_end = content.find('</div>', content.find('header-pool'))
        ui_end = content.find('</div>', ui_end + 5)
    
    # Add hamburger button
    hamburger_html = '\n      <button class="hamburger" id="hamburger-btn" aria-label="Menú" aria-expanded="false" style="display:none">\n        <span></span><span></span><span></span>\n      </button>\n'
    content = content[:ui_end] + hamburger_html + content[ui_end:]
    changes = True
    
    # Add mobile menu after header-pool closing
    pool_end = content.find('</div>', content.find('header-pool'))
    pool_end = content.find('</div>', pool_end + 5)
    content = content[:pool_end] + '\n' + MOBILE_MENU + '\n' + content[pool_end:]
    
    # Add JS
    # Fix: need pool-encargos-specific CSS for mobile menu positioning
    # The parent div isn't position:relative by default
    # Add style to header-pool
    content = content.replace(
        'background: white;',
        'background: white; position: relative;'
    )
    # Fix: pool header has no position:relative for the mobile-menu
    # Actually mobile-menu is absolute positioned relative to nearest positioned ancestor
    
    # Add JS
    content, c = add_js_if_missing(content)
    changes = changes or c
    
    return content, True


MOBILE_MENU_SIMPLE = """    <div class="mobile-menu" id="mobile-menu">
      <a href="/">Inicio</a>
      <a href="/#como-funciona">C\u00f3mo funciona</a>
      <a href="/blog/">Blog</a>
      <a href="/inmobiliarias.html">Inmobiliarias</a>
      <strong style="display:block;padding:.6rem 1.2rem;font-size:.82rem;color:#9aab8a;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #f0f0f0">T\u00e9cnicos</strong>
      <a href="/panel-tecnicos.html">Registro de t\u00e9cnicos</a>
      <a href="/pool-encargos.html">Trabajos</a>
      <a href="/blog/?cat=tecnicos">Blog t\u00e9cnico</a>
      <a href="/#presupuesto-card" class="btn-nav" style="margin:0 1rem 1rem;text-align:center">Presupuesto</a>
    </div>"""

def process_minimal_header(content):
    """Para 404.html y pago-exitoso.html que solo tienen logo sin nav."""
    if 'hamburger-btn' in content:
        return content, False
    changes = False
    
    # Add CSS
    content, c = add_css_if_missing(content, CSS_HAMBURGUESA)
    changes = changes or c
    
    # Add nav with hamburger inside header-inner
    logo_end = content.find('</a>', content.find('class="logo"'))
    nav_html = '\n    <nav class="nav">\n      <button class="hamburger" id="hamburger-btn" aria-label="Menú" aria-expanded="false">\n        <span></span><span></span><span></span>\n      </button>\n    </nav>\n'
    content = content[:logo_end+4] + nav_html + content[logo_end+4:]
    changes = True
    
    # Add menu after nav close
    nav_close = content.find('</nav>')
    content = content[:nav_close+6] + '\n' + MOBILE_MENU_SIMPLE + '\n' + content[nav_close+6:]
    
    # Add JS
    content, c = add_js_if_missing(content)
    changes = changes or c
    
    return content, True


def process_inmobiliarias(content):
    """inmobiliarias.html - add hamburger inside <nav> and menu after </nav>"""
    if 'hamburger-btn' in content:
        return content, False
    changes = False
    
    content, c = add_css_if_missing(content, CSS_HAMBURGUESA)
    changes = changes or c
    
    content, c = add_btn_in_nav(content)
    changes = changes or c
    
    content, c = add_menu_after_nav(content)
    changes = changes or c
    
    content, c = add_js_if_missing(content)
    changes = changes or c
    
    return content, True


def process_panel_tecnicos(content):
    """panel-tecnicos.html - add hamburger inside <nav> and menu after </nav>"""
    if 'hamburger-btn' in content:
        return content, False
    changes = False
    
    content, c = add_css_if_missing(content, CSS_HAMBURGUESA)
    changes = changes or c
    
    content, c = add_btn_in_nav(content)
    changes = changes or c
    
    content, c = add_menu_after_nav(content)
    changes = changes or c
    
    content, c = add_js_if_missing(content)
    changes = changes or c
    
    return content, True


def process_reforma_blog(content):
    """blog/reforma-certificado-energetico-2026-cambios.html - add hamburger"""
    if 'hamburger-btn' in content:
        return content, False
    changes = False
    
    content, c = add_css_if_missing(content, CSS_HAMBURGUESA)
    changes = changes or c
    
    content, c = add_btn_in_nav(content)
    changes = changes or c
    
    content, c = add_menu_after_nav(content)
    changes = changes or c
    
    content, c = add_js_if_missing(content)
    changes = changes or c
    
    return content, True


def process_contacto_enrich(content):
    """contacto.html - enrich existing mobile menu"""
    if 'hamburger-btn' not in content:
        return content, False
    # Add Inmobiliarias and Técnicos section to existing menu
    content, c = enrich_mobile_menu(content)
    return content, c


def process_blog_enrich(content):
    """blog/index.html and other blog pages - enrich mobile menu"""
    if 'hamburger-btn' not in content:
        return content, False
    content, c = enrich_mobile_menu(content)
    return content, c


# === MAIN ===
import os

files = {
    '/home/arturo/certificadoya/pool-encargos.html': process_pool_encargos,
    '/home/arturo/certificadoya/panel-tecnicos.html': process_panel_tecnicos,
    '/home/arturo/certificadoya/inmobiliarias.html': process_inmobiliarias,
    '/home/arturo/certificadoya/404.html': process_minimal_header,
    '/home/arturo/certificadoya/pago-exitoso.html': process_minimal_header,
    '/home/arturo/certificadoya/blog/reforma-certificado-energetico-2026-cambios.html': process_reforma_blog,
    '/home/arturo/certificadoya/contacto.html': process_contacto_enrich,
    '/home/arturo/certificadoya/blog/index.html': process_blog_enrich,
}

to_fix = {}
for f, processor in files.items():
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
        new_content, changed = processor(content)
        if changed:
            to_fix[f] = new_content
            print(f"✅  {os.path.relpath(f, '/home/arturo/certificadoya')}")
        else:
            print(f"⏭️  {os.path.relpath(f, '/home/arturo/certificadoya')} (sin cambios necesarios)")
    else:
        print(f"❌  {os.path.relpath(f, '/home/arturo/certificadoya')} (no existe)")

# Escribir cambios
for f, new_content in to_fix.items():
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(new_content)

print(f"\n=== Resumen: {len(to_fix)} archivos modificados ===")
for f in to_fix:
    print(f"  ✅  {os.path.relpath(f, '/home/arturo/certificadoya')}")
