#!/usr/bin/env python3
"""Transforma las 3 secciones del overlay móvil en acordeones retráctiles.
Enfoque: reemplazar TODO el contenido del <nav class="mobile-overlay-nav">
por la nueva estructura con accordions.
"""
import re, os, glob, sys

web_root = '/home/arturo/certificadoya'

# Patrón para encontrar las cabeceras de sección
HEADER_RE = re.compile(
    r'<strong style="display:block;padding:\.6rem 1\.2rem;font-size:\.82rem;color:#9aab8a;text-transform:uppercase;letter-spacing:\.05em;border-bottom:1px solid #f0f0f0">(🔑|🔧|🏢)(.+?)</strong>'
)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'mobile-overlay-nav' not in content:
        return False
    
    # Encontrar el nav
    nav_start = content.find('<nav class="mobile-overlay-nav">')
    if nav_start == -1:
        return False
    nav_tag_end = nav_start + len('<nav class="mobile-overlay-nav">')
    
    nav_close = content.find('</nav>', nav_tag_end)
    if nav_close == -1:
        return False
    
    # Extraer el contenido interior del nav
    inner = content[nav_tag_end:nav_close]
    
    # Encontrar todas las cabeceras con sus posiciones
    matches = list(HEADER_RE.finditer(inner))
    
    if not matches:
        return False
    
    # Construir nuevo contenido del nav
    new_inner_parts = []
    
    # Contenido antes de la primera cabecera (enlaces sueltos tipo FAQ/Blog)
    before_first = inner[:matches[0].start()].strip()
    if before_first:
        new_inner_parts.append(before_first)
    
    for i, m in enumerate(matches):
        header_full = m.group(0)
        icon = m.group(1)  # 🔑, 🔧, 🏢
        header_label = m.group(2).strip()  # "Propietarios", "Técnicos", "Inmobiliarias"
        
        # Texto completo de la cabecera
        header_text = icon + ' ' + header_label
        
        # Determinar contenido de la sección: desde después de esta cabecera hasta la siguiente o </nav>
        section_start = m.end()
        if i + 1 < len(matches):
            section_end = matches[i + 1].start()
        else:
            section_end = len(inner)
        
        section_raw = inner[section_start:section_end].strip()
        
        icon_map = {'🔑': 'propietarios', '🔧': 'tecnicos', '🏢': 'inmobiliarias'}
        slug = icon_map.get(icon, f'seccion-{i}')
        is_open = slug == 'propietarios'
        arrow_down = '\u25BE'
        arrow_right = '\u25B8'
        arrow_char = arrow_down if is_open else arrow_right
        
        # Indentar el contenido
        indented = '\n'.join(f'        {line.strip()}' for line in section_raw.split('\n') if line.strip())
        
        new_section = (
            f'\n<button class="accordion-toggle" onclick="toggleSection(\'{slug}\')" '
            f'aria-expanded="{"true" if is_open else "false"}" aria-controls="accordion-{slug}">'
            f'{header_text}'
            f'<span class="accordion-arrow">{arrow_char}</span>'
            f'</button>\n'
            f'<div class="accordion-content" id="accordion-{slug}" '
            f'style="display:{"block" if is_open else "none"}">\n'
            f'{indented}\n'
            f'</div>'
        )
        new_inner_parts.append(new_section)
    
    new_inner = '\n'.join(new_inner_parts) + '\n'
    new_content = content[:nav_tag_end] + '\n' + new_inner + '      ' + content[nav_close:]
    
    if new_content == content:
        return False
    
    # Añadir CSS si no existe
    css_to_add = '''  /* Acordeon overlay movil */
  .accordion-toggle{display:flex;align-items:center;justify-content:space-between;width:100%;padding:.8rem 1.2rem;font-size:.82rem;color:#9aab8a;text-transform:uppercase;letter-spacing:.05em;border:none;border-bottom:1px solid #f0f0f0;background:none;cursor:pointer;text-align:left;font-family:inherit}
  .accordion-toggle:hover{background:#f5f9f0}
  .accordion-toggle strong{margin:0;padding:0;border:none;display:inline;font-size:inherit;color:inherit;text-transform:inherit;letter-spacing:inherit}
  .accordion-arrow{font-size:.7rem;color:#9aab8a}
  .accordion-content{overflow:hidden}'''
    
    if '.accordion-toggle{' not in new_content:
        # Buscar donde insertar: después del último bloque de estilo del overlay
        # Insertar al final del bloque CSS de overlay
        overlay_css_end = new_content.rfind('/* Menú overlay móvil */')
        if overlay_css_end != -1:
            # Buscar el </style> más cercano después
            style_close = new_content.find('</style>', overlay_css_end)
            if style_close != -1:
                new_content = new_content[:style_close] + '\n' + css_to_add + '\n' + new_content[style_close:]
            else:
                # Fallback: añadir en el head
                new_content = new_content.replace('</head>', '<style>\n' + css_to_add + '\n</style>\n</head>')
    
    # Añadir JS si no existe
    js_to_add = '''
function toggleSection(id){var c=document.getElementById('accordion-'+id);var b=document.querySelector('[onclick*="'+id+'"]');if(!c||!b)return;var o=c.style.display!=='none';c.style.display=o?'none':'block';b.setAttribute('aria-expanded',!o);var a=b.querySelector('.accordion-arrow');if(a)a.textContent=o?'\u25B8':'\u25BE'}'''
    
    if 'function toggleSection' not in new_content:
        # Buscar el IIFE del overlay y añadir después
        iife_end = new_content.find('})();')
        if iife_end != -1:
            new_content = new_content[:iife_end+6] + '\n' + js_to_add + new_content[iife_end+6:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    html_files = glob.glob(os.path.join(web_root, '**/*.html'), recursive=True)
    count = 0
    errors = []
    
    for fpath in sorted(html_files):
        if 'node_modules' in fpath:
            continue
        try:
            if process_file(fpath):
                rel = os.path.relpath(fpath, web_root)
                print(f"  {chr(10003)} {rel}")
                count += 1
        except Exception as e:
            rel = os.path.relpath(fpath, web_root)
            print(f"  {chr(10007)} {rel}: {e}", file=sys.stderr)
            errors.append(rel)
    
    print(f"\n=== {count} archivos modificados ===")
    if errors:
        print(f"Errores: {len(errors)}", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
